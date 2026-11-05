(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const stage = $('#stage'), board = $('#board'), view = $('#view'), overlay = $('#overlay');
  let display = { rotate: 'auto', tier: 'auto', viewport: {}, show_last_play: true };
  let displayKey = '', seq = -1, lastKey = '', lastIdent = '', lastScores = {};
  let queue = [], playing = false, timer = null, inflight = false, wifiAvail = false;

  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // ---------- sizing, rotation, tier ----------
  function layout() {
    const vw = innerWidth, vh = innerHeight;
    let rot = display.rotate;
    rot = (rot === 'auto' || rot == null) ? (vh > vw * 1.2 ? 90 : 0) : Number(rot);
    const side = rot === 90 || rot === 270;
    const LW = side ? vh : vw, LH = side ? vw : vh;
    Object.assign(stage.style, { width: LW + 'px', height: LH + 'px', left: (vw - LW) / 2 + 'px', top: (vh - LH) / 2 + 'px', transform: `rotate(${rot}deg)` });
    const vp = display.viewport || {};
    const w = vp.width > 0 ? Math.min(vp.width, LW) : LW;
    const h = vp.height > 0 ? Math.min(vp.height, LH) : LH;
    Object.assign(board.style, { left: (vp.width > 0 ? vp.x || 0 : 0) + 'px', top: (vp.height > 0 ? vp.y || 0 : 0) + 'px', width: w + 'px', height: h + 'px' });
    let tier = display.tier;
    if (!['compact', 'bar', 'wide', 'standard'].includes(tier)) {
      // standard = regular-shaped screens (7" 1024x600, 800x480, 4:3); the rest are ultrawide bars
      tier = w / h < 2.3 ? 'standard' : (w < 1000 || h < 300) ? 'compact' : (w >= 1700 && h >= 440) ? 'wide' : 'bar';
    }
    board.dataset.tier = tier;
    rotation = rot;
    // 1u = 1% of height, capped so a 320u-wide (bar) or 170u-wide (standard) design always fits
    board.style.setProperty('--u', Math.min(h / 100, w / (tier === 'standard' ? 170 : 320)) + 'px');
    board.classList.toggle('showlp', !!display.show_last_play);
    fitEndzones();
  }
  let rotation = 0;
  addEventListener('resize', layout);

  // ---------- pieces ----------
  const BALL = '<svg class="fb" viewBox="0 0 40 24"><ellipse cx="20" cy="12" rx="18.5" ry="10.5" fill="#8b4a1c" stroke="#fff" stroke-width="1.6"/><path d="M12 12h16M16 9v6M20 9v6M24 9v6" stroke="#fff" stroke-width="1.7" stroke-linecap="round"/></svg>';
  const GOALPOST = '<svg viewBox="0 0 100 125"><path d="M50 125V72M18 72h64M18 72V4M82 72V4" stroke="#ffd21f" stroke-width="6" fill="none" stroke-linecap="round"/><ellipse class="kb" cx="50" cy="114" rx="6.5" ry="4.2" fill="#8b4a1c" stroke="#fff" stroke-width="1.2"/></svg>';

  function logo(t, cls = '') {
    const img = t.logo ? `<img src="${esc(t.logo)}" alt="" onerror="this.parentNode.classList.add('nologo');this.remove()">` : '';
    return `<div class="logo ${cls} ${t.logo ? '' : 'nologo'}" data-abbr="${esc(t.abbr)}" style="--tc:${esc(t.color)};--ta:${esc(t.alt || '#999')}">${img}</div>`;
  }

  function kickoff(ts) {
    if (!ts) return { time: 'TBD', day: '' };
    const d = new Date(ts * 1000), now = new Date();
    const time = d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    const days = Math.round((new Date(d.toDateString()) - new Date(now.toDateString())) / 864e5);
    const day = days === 0 ? 'TODAY' : days === 1 ? 'TOMORROW'
      : d.toLocaleDateString([], { weekday: 'short', month: 'numeric', day: 'numeric' }).toUpperCase();
    return { time, day };
  }

  function teamRow(g, side, favSides) {
    const t = g[side], o = g[side === 'home' ? 'away' : 'home'];
    const live = g.state === 'in';
    const cls = [favSides.includes(side) ? 'fav' : '',
      g.state === 'post' && t.score < o.score ? 'lose' : '',
      g.state === 'post' && t.score > o.score ? 'win' : ''].join(' ');
    const pips = live && t.timeouts != null
      ? `<span class="pips">${[0, 1, 2].map(i => `<i class="pip ${i < t.timeouts ? 'on' : ''}"></i>`).join('')}</span>` : '';
    return `<div class="row ${cls}" style="--tc:${esc(t.color)};--ta:${esc(t.alt)}">
      <div class="stripe"></div>${logo(t)}
      <div class="ident"><div class="abbr" data-name="${esc((t.name || '').toUpperCase())}">${esc(t.abbr)}</div>
        <div class="sub"><span>${esc(t.record)}</span>${pips}</div></div>
      <div class="poss">${live && g.possession === side ? BALL : ''}</div>
      <div class="score" data-k="${esc(g.id)}-${side}">${g.state === 'pre' ? '' : t.score}</div></div>`;
  }

  function statusPanel(g, label) {
    if (g.state === 'pre') {
      const k = kickoff(g.start_ts);
      return `<div class="st pre"><div class="lbl">KICKOFF</div><div class="big">${esc(k.time)}</div>
        <div class="mid">${esc(k.day)}</div>${g.broadcast ? `<div class="small">${esc(g.broadcast)}</div>` : ''}</div>`;
    }
    if (g.state === 'post') return `<div class="st post">${label ? `<div class="lbl">${esc(label)}</div>` : ''}<div class="final">${esc((g.detail || 'Final').toUpperCase())}</div></div>`;
    if (['STATUS_HALFTIME', 'STATUS_END_PERIOD'].includes(g.status_name))
      return `<div class="st brk"><div class="final">${esc((g.detail || '').toUpperCase())}</div></div>`;
    const dir = g.possession === 'away' ? 'r' : 'l';
    const field = g.ball_x == null ? '' : `<div class="field"><div style="background:${esc(g.away.color)}"></div>
      <div class="turf">${g.first_down_x != null ? `<div class="fd" style="left:${g.first_down_x}%"></div>` : ''}
      <div class="ball ${dir}" style="left:${g.ball_x}%"></div></div><div style="background:${esc(g.home.color)}"></div></div>`;
    return `<div class="st live ${g.red_zone ? 'rz' : ''}">
      <div class="clock"><span class="per">${esc(g.period_label)}</span><span class="time">${esc(g.clock)}</span></div>
      <div class="dd">${esc(g.down_text || ' ')}</div>
      <div class="spot">${g.spot ? `<span>BALL ON ${esc(g.spot)}</span>` : ''}${g.red_zone ? '<span class="rztag">RED ZONE</span>' : ''}</div>
      ${field}<div class="lastplay">${esc(g.last_play)}</div></div>`;
  }

  const renderGame = sc => `<div class="game"><div class="teams">${teamRow(sc.game, 'away', sc.fav_sides || [])}${teamRow(sc.game, 'home', sc.fav_sides || [])}</div>${statusPanel(sc.game, sc.label)}</div>`;

  // ---------- live field view ----------
  // x = 0 is the AWAY team's goal line, x = 100 the HOME team's. The away team attacks right.
  function fieldHTML(sc) {
    const th = sc.field;
    const nums = [10, 20, 30, 40, 50, 60, 70, 80, 90].map(y => {
      const n = y <= 50 ? y : 100 - y;
      const arrow = y < 50 ? 'al' : y > 50 ? 'ar' : '';
      return `<b class="num bot ${arrow}" style="left:${y}%">${n}</b><b class="num top ${arrow}" style="left:${y}%">${n}</b>`;
    }).join('');
    const ez = (txt, side) => `<div class="ez ${side}"><span data-len="${txt.length}">${esc(txt.toUpperCase())}</span></div>`;
    const city = th.city || th.abbr, nick = th.name || th.abbr;
    return `<div class="fv bug-${esc(sc.score_bug)} angle-${esc(sc.field_angle)}" style="--fc:${esc(th.color)};--fa:${esc(th.alt)}">
      <div class="stands"></div>
      <div class="pitch"><div class="turf3">
        ${ez(city, 'l')}
        <div class="pf">
          <div class="mow"></div><div class="ylines"></div><div class="hash h1"></div><div class="hash h2"></div>
          ${nums}
          <div class="midlogo ${th.logo ? '' : 'nologo'}" data-abbr="${esc(th.abbr)}">${th.logo ? `<img src="${esc(th.logo)}" alt="" onerror="this.parentNode.classList.add('nologo');this.remove()">` : ''}</div>
          <div class="rzone l"></div><div class="rzone r"></div>
          <div class="drive"></div><div class="los"></div><div class="fdl"></div>
          <div class="fball"><span class="chip"></span>${BALL}</div>
        </div>
        ${ez(nick, 'r')}
      </div></div>
      <div class="bug"></div></div>`;
  }

  function fitEndzones() {
    // size end zone words to the actual end zone box, whatever the screen
    view.querySelectorAll('.ez span').forEach(s => {
      const ez = s.parentNode, len = Number(s.dataset.len) || 6;
      const across = ez.offsetWidth, along = ez.offsetHeight;
      if (!across || !along) return;
      s.style.fontSize = Math.min(across * 0.66, (along * 0.88) / (len * 0.56)) + 'px';
    });
  }

  function bugTeam(g, side) {
    const t = g[side], poss = g.possession === side;
    const pips = t.timeouts != null ? `<span class="tos">${[0, 1, 2].map(i => `<i class="${i < t.timeouts ? 'on' : ''}"></i>`).join('')}</span>` : '';
    return `<div class="bt ${poss ? 'poss' : ''}" style="--tc:${esc(t.color)};--ta:${esc(t.alt)}">
      ${logo(t)}<div class="bn2"><span class="ab">${esc(t.abbr)}${poss ? BALL : ''}</span>${pips}</div>
      <div class="sc" data-k="${esc(g.id)}-${side}">${t.score}</div></div>`;
  }

  function patchField(sc) {
    const g = sc.game, fv = view.querySelector('.fv');
    if (!fv) return;
    const pf = fv.querySelector('.pf');
    const show = (sel, on) => pf.querySelector(sel).classList.toggle('hide', !on);
    const has = g.ball_x != null && g.possession;
    show('.fball', has); show('.los', has);
    if (has) {
      pf.querySelector('.fball').style.left = g.ball_x + '%';
      pf.querySelector('.los').style.left = g.ball_x + '%';
      const off = g[g.possession];
      const chip = pf.querySelector('.chip');
      chip.textContent = g.possession === 'away' ? `${off.abbr} ▸` : `◂ ${off.abbr}`;
      chip.style.background = off.color;
      chip.style.borderColor = off.alt;
    }
    const fd = g.first_down_x;
    show('.fdl', has && fd != null && fd > 0 && fd < 100);
    if (fd != null) pf.querySelector('.fdl').style.left = fd + '%';
    const ds = g.drive_start_x;
    show('.drive', has && ds != null && ds !== g.ball_x);
    if (has && ds != null) {
      const d = pf.querySelector('.drive'), off = g[g.possession];
      d.style.left = Math.min(ds, g.ball_x) + '%';
      d.style.width = Math.abs(g.ball_x - ds) + '%';
      d.style.setProperty('--dc', off.color);
      d.classList.toggle('toleft', g.possession === 'home');
    }
    show('.rzone.r', g.red_zone && g.possession === 'away');
    show('.rzone.l', g.red_zone && g.possession === 'home');
    // score bug
    const dd = g.down_text || (['STATUS_END_PERIOD'].includes(g.status_name) ? (g.detail || '').toUpperCase() : '');
    fv.querySelector('.bug').innerHTML = `${bugTeam(g, 'away')}${bugTeam(g, 'home')}
      <div class="bc"><span class="per">${esc(g.period_label)}</span><span class="time">${esc(g.clock)}</span></div>
      <div class="bd ${g.red_zone ? 'rz' : ''} ${dd ? '' : 'empty'}">${esc(dd || ' ')}</div>
      <div class="bi"><span class="spot2">${g.spot ? 'BALL ON ' + esc(g.spot) : ''}</span>
        <span class="lp">${display.show_last_play ? esc(g.last_play) : ''}</span></div>`;
  }

  // ---------- score grid & standings layouts ----------
  function tile(g) {
    const line = side => {
      const t = g[side], o = g[side === 'home' ? 'away' : 'home'];
      const cls = g.state === 'post' ? (t.score > o.score ? 'win' : t.score < o.score ? 'lose' : '') : '';
      return `<div class="tl ${cls}" style="--tc:${esc(t.color)};--ta:${esc(t.alt)}"><i class="stripe"></i>${logo(t)}
        <span class="ab">${esc(t.abbr)}</span><span class="tsc">${g.state === 'pre' ? '' : t.score}</span></div>`;
    };
    const status = g.state === 'pre' ? kickoff(g.start_ts).time : g.state === 'in' ? `${g.period_label} ${g.clock}` : (g.detail || 'Final');
    return `<div class="tile ${g.state === 'in' ? 'live' : ''}" data-game="${esc(g.id)}"><div class="tlines">${line('away')}${line('home')}</div><div class="tst">${esc(status.toUpperCase())}</div></div>`;
  }

  const byeTile = (t, label) => `<div class="tile bye" style="--tc:${esc(t.color)}"><div class="tl"><i class="stripe"></i>${logo(t)}
      <span class="ab">${esc(t.abbr)}</span></div><div class="tst">BYE${label ? '<br>' + esc(label) : ''}</div></div>`;
  const renderScores = sc => `<div class="sgrid"><div class="sh"><span class="dv">${esc(sc.division ? sc.division.toUpperCase() : (sc.label || 'SCORES'))}</span>
      <span class="lbl">${esc(sc.live ? 'LIVE · ' + (sc.label || '') + ' · TAP A GAME' : sc.division ? (sc.label || '') + ' FINALS' : 'FINAL SCORES ' + (sc.page || ''))}</span></div>
      <div class="tiles">${sc.games.map(tile).join('')}${(sc.byes || []).map(t => byeTile(t, sc.label)).join('')}</div></div>`;

  // a favorite with no game this week
  const renderBye = sc => { const t = sc.team; return `<div class="byescr" style="--tc:${esc(t.color)};--ta:${esc(t.alt)}">
      ${logo(t, 'big')}<div class="bx-t"><div class="bx-n">${esc(t.full || t.name)}</div>
      <div class="bx-w">BYE <span>${esc(sc.label || '')}</span></div>
      ${t.record ? `<div class="bx-r">${esc(t.record)} · ${esc((sc.division || '').toUpperCase())}</div>` : ''}</div></div>`; };

  const rec = r => `${r.w}-${r.l}${r.t ? '-' + r.t : ''}`;

  function renderStandingsGrid(sc) {
    const favs = sc.favorites || [];
    const cols = sc.divisions.map(d => `<div class="gcol"><div class="gh">${esc(d.name.split(' ').slice(1).join(' ').toUpperCase())}</div>
      ${d.rows.map(r => `<div class="gr ${favs.includes(r.abbr) ? 'fav' : ''}" style="--tc:${esc(r.color)}">${logo({ ...r, alt: '#fff' })}
        <span class="ab">${esc(r.abbr)}</span><span class="wl">${rec(r)}</span></div>`).join('')}</div>`).join('');
    return `<div class="sgrid2"><div class="sh"><span class="dv">${esc(sc.title)}</span><span class="lbl">BY DIVISION</span></div>
      <div class="gcols" style="grid-template-columns:repeat(${sc.divisions.length},1fr)">${cols}</div></div>`;
  }

  function renderRanked(sc) {
    const favs = sc.favorites || [];
    const rows = sc.rows.map((r, i) => `<div class="rr ${favs.includes(r.abbr) ? 'fav' : ''}" style="--tc:${esc(r.color)}">
      <span class="rk">${sc.seeds ? r.seed : sc.start + i}</span>${logo({ ...r, alt: '#fff' })}<span class="nm">${esc(r.name)}</span>
      <span class="wl">${rec(r)}</span></div>`).join('');
    return `<div class="sranked"><div class="sh"><span class="dv">${esc(sc.title)}</span>
      <span class="lbl">${sc.seeds ? 'PLAYOFF SEEDS ' : ''}${sc.start}–${sc.start + sc.rows.length - 1}</span></div><div class="rcols">${rows}</div></div>`;
  }

  function renderStandings(sc) {
    const favs = sc.favorites || [];
    const pct = p => (p >= 1 ? '1.000' : p.toFixed(3).replace(/^0/, ''));
    const rows = (sc.rows || []).map((r, i) => `<div class="sr ${favs.includes(r.abbr) ? 'fav' : ''}" style="--tc:${esc(r.color)}">
      <span class="rk">${i + 1}</span>${logo({ ...r, alt: '#fff' })}<span>${esc(r.name)}</span>
      <span class="wl">${r.w}-${r.l}${r.t ? '-' + r.t : ''}</span><span class="pct">${pct(r.pct || 0)}</span></div>`).join('');
    return `<div class="standings"><div class="sh"><span class="dv">${esc(sc.division.toUpperCase())}</span><span class="lbl">STANDINGS</span></div><div class="sr-list">${rows}</div></div>`;
  }

  const clockText = () => new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  const renderIdle = () => `<div class="idle"><div class="t" id="idleclock">${clockText()}</div><div class="m">NO GAMES RIGHT NOW</div></div>`;
  setInterval(() => { const c = $('#idleclock'); if (c) c.textContent = clockText(); }, 1000);

  let lastFieldKey = '';
  function render(sc) {
    board.classList.toggle('pinned', sc.mode === 'pinned');
    const key = JSON.stringify(sc) + display.show_last_play;
    if (key === lastKey) return;
    lastKey = key;
    const ident = sc.type + ':' + (sc.view || '') + ':' + (sc.game ? sc.game.id : sc.division || sc.title || sc.label || '') + ':' + (sc.start || sc.page || '');
    view.classList.toggle('noanim', ident === lastIdent);
    lastIdent = ident;
    const bumps = [];
    if (sc.type === 'game') {
      const g = sc.game;
      for (const s of ['away', 'home']) {
        const k = `${g.id}-${s}`, v = g[s].score;
        if (g.state === 'in' && lastScores[k] !== undefined && v > lastScores[k]) bumps.push(k);
        lastScores[k] = v;
      }
    }
    if (sc.type === 'game' && sc.view === 'field') {
      // keep the field on screen and move things on it, so the ball slides between plays
      const fkey = ident + JSON.stringify(sc.field) + sc.field_angle + sc.score_bug;
      if (fkey !== lastFieldKey || !view.querySelector('.fv')) {
        view.innerHTML = fieldHTML(sc);
        fitEndzones();
        lastFieldKey = fkey;
      }
      patchField(sc);
    } else {
      lastFieldKey = '';
      const R = { game: renderGame, standings: renderStandings, scores: renderScores, bye: renderBye,
        standings_grid: renderStandingsGrid, standings_ranked: renderRanked }[sc.type] || renderIdle;
      view.innerHTML = R(sc);
    }
    bumps.forEach(k => view.querySelector(`[data-k="${k}"]`)?.classList.add('bump'));
  }

  // ---------- event animations ----------
  const FULL = new Set(['touchdown', 'field_goal', 'safety', 'two_point', 'turnover', 'final', 'score']);
  const DUR = { touchdown: 6500, field_goal: 4800, safety: 4500, two_point: 4000, turnover: 4500, final: 4500, score: 3500,
    first_down: 2600, red_zone: 2800, extra_point: 2200, kickoff: 2600, halftime: 2800 };

  function tplFull(e) {
    const t = e.abbr ? { abbr: e.abbr, color: e.color, alt: e.alt, logo: e.logo } : null;
    const letters = [...e.label].map((c, i) => `<span style="animation-delay:${(0.25 + i * 0.05).toFixed(2)}s">${c === ' ' ? '&nbsp;' : esc(c)}</span>`).join('');
    const sub = e.kind === 'final' ? e.score
      : e.kind === 'turnover' ? `${e.name || e.abbr} BALL`
      : e.kind === 'field_goal' ? `IT'S GOOD · ${e.name || ''}`
      : e.kind === 'touchdown' ? `${e.name || ''} +${e.points || 6}`
      : (e.name || '');
    const left = e.kind === 'field_goal' ? `<div class="post">${GOALPOST}</div>` : (t ? logo(t, 'ovlogo') : '');
    const right = e.kind === 'field_goal' && t ? logo(t, 'ovlogo') : '';
    return `<div class="stripes"></div><div class="flash"></div>
      <div class="ov">${left}<div class="ovt"><div class="ovtext ${e.label.length > 10 ? 'long' : ''}">${letters}</div>
      <div class="ovsub">${esc(sub.toUpperCase())}</div></div>${right}</div><div class="ovbar"></div>`;
  }

  function tplBanner(e) {
    const t = e.abbr ? { abbr: e.abbr, color: e.color, alt: e.alt, logo: e.logo } : null;
    return `<div class="bn">${t && e.kind !== 'first_down' ? logo(t) : ''}<span class="bntext">${esc(e.label)}</span>${e.abbr ? `<span class="bnsub">${esc(e.abbr)}</span>` : ''}</div>`;
  }

  function next() {
    const e = queue.shift();
    if (!e) { playing = false; overlay.className = ''; overlay.innerHTML = ''; return; }
    playing = true;
    overlay.style.setProperty('--tc', e.color || '#1b2330');
    overlay.style.setProperty('--ta', e.alt || '#ffd21f');
    overlay.className = `show ${FULL.has(e.kind) ? 'full' : 'banner'} k-${e.kind}`;
    overlay.innerHTML = FULL.has(e.kind) ? tplFull(e) : tplBanner(e);
    if (e.kind === 'red_zone') board.classList.add('rzpulse');
    setTimeout(() => {
      overlay.classList.add('out');
      setTimeout(() => { board.classList.remove('rzpulse'); next(); }, 400);
    }, DUR[e.kind] || 3000);
  }

  function enqueue(e) {
    if (queue.length > 4) queue = queue.filter(x => FULL.has(x.kind)); // drop small stuff if we fall behind
    queue.push(e);
    if (!playing) next();
  }

  // ---------- polling ----------
  function schedule(ms) { clearTimeout(timer); timer = setTimeout(poll, ms); }

  async function poll() {
    if (inflight) return schedule(500);
    inflight = true;
    try {
      const r = await fetch(`/api/state?since=${seq}`, { cache: 'no-store' });
      const d = await r.json();
      const dk = JSON.stringify(d.display);
      if (dk !== displayKey) { displayKey = dk; display = d.display; layout(); }
      d.events.forEach(enqueue);
      seq = d.seq;
      render(d.screen);
      if (d.wifi) { wifiAvail = !!d.wifi.available; offlineScreen(d.wifi); }
      $('#net').classList.toggle('bad', !d.status.ok);
    } catch (err) {
      $('#net').classList.add('bad');
    } finally {
      inflight = false;
      schedule(2000);
    }
  }

  const post = (url, body) => fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });

  // Keyboard (handy on a laptop, or a USB keypad on the Pi)
  // Touch / click: left third = previous game, right third = next, middle = back to Auto
  const toast = document.createElement('div');
  toast.id = 'toast';
  board.appendChild(toast);
  let toastTimer;
  function showToast(t) {
    toast.textContent = t;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 1100);
  }
  // ---------- on-screen quick settings: press and hold anywhere for ~1 second ----------
  const MENU = [
    ['Live game', 'live_view', [['field', 'Field'], ['scoreboard', 'Scoreboard']]],
    ['Field angle', 'field_angle', [['tv', 'TV tilt'], ['flat', 'Flat']]],
    ['Score bar', 'score_bug', [['bottom', 'Bottom'], ['top', 'Top']]],
    ['Field colors', 'field_theme', [['home', 'Home team'], ['favorite', 'Favorite']]],
    ['Other live games', 'other_live_mode', [['grid', 'By division'], ['live', 'Gamecast']]],
    ['Change every', 'rotate_seconds', [[8, '8s'], [12, '12s'], [20, '20s'], [30, '30s']]],
    ['Screen', 'rotate', [['auto', 'Normal'], ['180', 'Upside down']]],
  ];
  const menu = document.createElement('div');
  menu.id = 'menu';
  board.appendChild(menu);
  let settings = {}, menuTimer, qrOk = true, menuArmed = false, menuClosedAt = -1e9;
  const menuOpen = () => menu.classList.contains('show');
  function closeMenu() { menu.classList.remove('show'); clearTimeout(menuTimer); menuClosedAt = performance.now(); }
  function bumpMenu() { clearTimeout(menuTimer); menuTimer = setTimeout(closeMenu, 30000); }  // closes itself if left open
  function drawMenu(info) {
    const rows = MENU.map(([label, key, opts]) => `<div class="mrow"><div class="mlab">${esc(label)}</div><div class="mopts">${
      opts.map(([v, t]) => `<button data-k="${key}" data-v="${v}" class="${String(settings[key]) === String(v) ? 'on' : ''}">${esc(t)}</button>`).join('')
    }</div></div>`).join('');
    const url = info && info.settings_url;
    menu.innerHTML = `<div class="mpanel"><div class="mhead">QUICK SETTINGS</div>${rows}
      <div class="mbtns"><button data-act="lock">Lock this game</button><button data-act="auto">Back to Auto</button>${wifiAvail ? '<button data-act="wifi">Wi-Fi</button>' : ''}<button data-act="close" class="done">Done</button></div></div>
      <div class="mside">${url && qrOk ? `<img class="mqr" src="/api/qr.svg" alt="" onerror="this.remove()">` : ''}
      <div class="mhint">All settings<br>on your phone</div><div class="murl">${esc(url ? url.replace('http://', '') : '')}</div></div>`;
  }
  async function openMenu() {
    try { settings = await (await fetch('/api/settings', { cache: 'no-store' })).json(); } catch (e) { settings = {}; }
    let info = null;
    try { info = await (await fetch('/api/info', { cache: 'no-store' })).json(); } catch (e) {}
    drawMenu(info);
    menuArmed = false;            // the finger that opened the menu is still down: ignore its release
    menu.classList.add('show');
    bumpMenu();
  }
  // menu buttons act on finger/mouse RELEASE over the same button (works whether the panel reports touch or mouse)
  let menuDownBtn = null;
  menu.addEventListener('pointerdown', ev => { menuDownBtn = ev.target.closest('button'); }, true);
  menu.addEventListener('click', ev => { ev.stopPropagation(); ev.preventDefault(); });
  menu.addEventListener('pointerup', async ev => {
    ev.stopPropagation();
    bumpMenu();
    if (!menuArmed) return;          // a press must start inside the open menu (not the long-press that opened it)
    const b = ev.target.closest('button');
    if (!b || b !== menuDownBtn) return;
    menuDownBtn = null;
    if (!b) return;                  // only Done closes the menu, so a stray touch can't
    if (b.dataset.act === 'close') return closeMenu();
    if (b.dataset.act === 'auto') { post('/api/control', { action: 'auto' }).then(() => schedule(30)); showToast('AUTO'); return closeMenu(); }
    if (b.dataset.act === 'wifi') { closeMenu(); openWifi(); return; }
    if (b.dataset.act === 'lock') { post('/api/control', { action: 'lock' }).then(() => schedule(30)); showToast('LOCKED'); return closeMenu(); }
    const k = b.dataset.k, v = /^\d+$/.test(b.dataset.v) && k === 'rotate_seconds' ? Number(b.dataset.v) : b.dataset.v;
    b.parentElement.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
    settings[k] = v;
    await post('/api/settings', { [k]: v });
    schedule(30);
  });
  menu.addEventListener('pointerdown', ev => { ev.stopPropagation(); menuArmed = true; });

  // hold to open the menu; a quick tap flips to the next/previous screen (no lock)
  let holdTimer = null, held = false, downAt = null;
  board.addEventListener('pointerdown', ev => {
    if (menuOpen() || wifiOpen()) return;
    held = false; downAt = [ev.clientX, ev.clientY];
    clearTimeout(holdTimer);
    holdTimer = setTimeout(() => { held = true; openMenu(); }, 900);
  });
  board.addEventListener('pointermove', ev => {
    if (downAt && Math.hypot(ev.clientX - downAt[0], ev.clientY - downAt[1]) > 25) clearTimeout(holdTimer);
  });
  ['pointerup', 'pointercancel', 'pointerleave'].forEach(t => board.addEventListener(t, () => { clearTimeout(holdTimer); downAt = null; }));
  board.addEventListener('contextmenu', ev => ev.preventDefault());   // long-press on a touch screen
  addEventListener('selectstart', ev => ev.preventDefault());           // no text selection on a kiosk
  addEventListener('dragstart', ev => ev.preventDefault());

  // ---------- tap controls: one tap shows a bar of buttons; tap a score tile to open that game ----------
  const bar = document.createElement('div');
  bar.id = 'ctlbar';
  bar.innerHTML = `<button data-c="prev">\u25C0 Prev</button><button data-c="auto">Auto</button>
    <button data-c="next">Next \u25B6</button><button data-c="menu">\u2699 Settings</button>`;
  board.appendChild(bar);
  let barTimer, barDownBtn = null, barShownAt = -1e9;
  const barOpen = () => bar.classList.contains('show');
  function hideBar() { bar.classList.remove('show'); clearTimeout(barTimer); }
  function showBar() {
    const locked = board.classList.contains('pinned');
    bar.querySelector('[data-c=auto]').textContent = locked ? '\u21A9 Back' : 'Auto';
    bar.classList.add('show'); barShownAt = performance.now();
    clearTimeout(barTimer); barTimer = setTimeout(hideBar, 6000);
  }
  bar.addEventListener('pointerdown', ev => { ev.stopPropagation(); barDownBtn = ev.target.closest('button'); });
  bar.addEventListener('click', ev => { ev.stopPropagation(); ev.preventDefault(); });
  bar.addEventListener('pointerup', ev => {
    ev.stopPropagation();
    const b = ev.target.closest('button');
    if (!b || b !== barDownBtn) return;
    barDownBtn = null;
    const c = b.dataset.c;
    if (c === 'menu') { hideBar(); openMenu().then(() => { menuArmed = true; }); return; }
    showToast({ prev: '\u25C0 PREV', next: 'NEXT \u25B6', auto: 'AUTO' }[c]);
    post('/api/control', { action: c }).then(() => schedule(30));
    clearTimeout(barTimer); barTimer = setTimeout(hideBar, 6000);   // keep it up while you flip
  });

  board.addEventListener('click', ev => {
    if (held) { held = false; return; }   // that press opened the menu
    if (menuOpen() || wifiOpen() || performance.now() - menuClosedAt < 600) return;   // the tap that closed the menu
    const t = ev.target.closest('.tile[data-game]');
    if (t) {                               // a game on a score screen: open its gamecast
      hideBar();
      showToast('GAMECAST');
      post('/api/control', { action: 'pin', game_id: t.dataset.game }).then(() => schedule(30));
      return;
    }
    if (barOpen() && performance.now() - barShownAt > 300) hideBar(); else showBar();
  });

  // ---------- Wi-Fi setup on the screen (list of networks, on-screen keyboard, connect) ----------
  // A button acts on release over the same button (reliable with this touch panel).
  function onTap(el, fn) {
    let down = null;
    el.addEventListener('pointerdown', ev => { ev.stopPropagation(); down = ev.target.closest('button'); });
    el.addEventListener('click', ev => { ev.stopPropagation(); ev.preventDefault(); });
    el.addEventListener('pointerup', ev => {
      ev.stopPropagation();
      const b = ev.target.closest('button');
      if (b && b === down) fn(b);
      down = null;
    });
  }
  const wifi = document.createElement('div');
  wifi.id = 'wifi';
  board.appendChild(wifi);
  const wifiOpen = () => wifi.classList.contains('show');
  const LOCK = '<svg class="lk" viewBox="0 0 16 20"><rect x="1.5" y="8.5" width="13" height="10" rx="2" fill="currentColor"/><path d="M4.5 9V6a3.5 3.5 0 0 1 7 0v3" fill="none" stroke="currentColor" stroke-width="2.2"/></svg>';
  let wf = { view: 'list', nets: [], ssid: '', text: '', show: false, layer: 'lower', step: 'psk', msg: '', st: {} };
  const bars = sig => sig == null ? '' : sig > -55 ? '▂▄▆█' : sig > -67 ? '▂▄▆' : sig > -78 ? '▂▄' : '▂';
  const KB = {
    lower: ['1234567890', 'qwertyuiop', 'asdfghjkl', ['SHIFT', ...'zxcvbnm', 'BKSP'], ['SYM', '-', 'SPACE', '_', '.']],
    upper: ['1234567890', 'QWERTYUIOP', 'ASDFGHJKL', ['SHIFT', ...'ZXCVBNM', 'BKSP'], ['SYM', '-', 'SPACE', '_', '.']],
    sym: ['1234567890', '!@#$%^&*()', '-_=+[]{}\\|', [...';:\'",<>/?', 'BKSP'], ['ABC', '`', '~', 'SPACE', '.']],
  };
  const keyLabel = { SHIFT: '⇧', BKSP: '⌫', SYM: '#+=', ABC: 'ABC', SPACE: 'space' };
  function keyboard() {
    return `<div class="kb">${KB[wf.layer].map(row => `<div class="kr">${[...row].map(k =>
      `<button class="k ${k.length > 1 ? 'k-' + k.toLowerCase() : ''} ${k === 'SHIFT' && wf.layer === 'upper' ? 'on' : ''}" data-key="${esc(k)}">${esc(keyLabel[k] || k)}</button>`).join('')}</div>`).join('')}</div>`;
  }
  function drawWifi() {
    const st = wf.st || {};
    const head = `<div class="wh"><span class="wt">WI-FI</span><span class="ws">${st.connected ? `Connected to <b>${esc(st.ssid)}</b> · ${esc(st.ip || '')}` : 'Not connected'}</span>
      <button data-w="close">Close</button></div>`;
    let body = '';
    if (wf.view === 'list') {
      const rows = wf.nets.length ? wf.nets.map(n => `<button class="wn ${n.ssid === st.ssid ? 'cur' : ''}" data-w="pick" data-ssid="${esc(n.ssid)}" data-secure="${n.secure ? 1 : 0}">
          <span class="nm">${esc(n.ssid)}</span><span class="sg">${n.secure ? LOCK : ''}${bars(n.signal)}</span></button>`).join('')
        : `<div class="wmsg">${esc(wf.msg || 'Looking for networks…')}</div>`;
      body = `<div class="wl">${rows}</div><div class="wb"><button data-w="scan">Rescan</button><button data-w="other">Other network…</button></div>`;
    } else if (wf.view === 'type') {
      const shown = wf.step === 'ssid' || wf.show ? esc(wf.text) : '•'.repeat(wf.text.length);
      const label = wf.step === 'ssid' ? 'Network name' : `Password for <b>${esc(wf.ssid)}</b>`;
      body = `<div class="wf"><div class="wlab">${label}</div><div class="wbox">${shown}<i class="caret"></i></div>
        ${wf.step === 'psk' ? `<button data-w="showpw">${wf.show ? 'Hide' : 'Show'}</button>` : ''}</div>${keyboard()}
        <div class="wb"><button data-w="back">Back</button><button data-w="go" class="go">${wf.step === 'ssid' ? 'Next' : 'Connect'}</button></div>`;
    } else {
      const a = wf.st.attempt || {};
      const txt = a.state === 'ok' ? `✓ Connected to <b>${esc(a.ssid)}</b>${a.ip ? ' · ' + esc(a.ip) : ''}` :
        a.state === 'failed' ? `✗ ${esc(a.error || "Couldn't connect.")}` : `Connecting to <b>${esc(wf.ssid)}</b>…<br><small>This can take up to a minute.</small>`;
      body = `<div class="wmsg big">${txt}</div><div class="wb">${a.state === 'failed' ? '<button data-w="retry">Try again</button><button data-w="list">Networks</button>' : ''}
        ${a.state === 'ok' ? '<button data-w="close" class="go">Done</button>' : ''}</div>`;
    }
    wifi.innerHTML = head + `<div class="wbody">${body}</div>`;
  }
  async function wifiStatus() { try { wf.st = await (await fetch('/api/wifi', { cache: 'no-store' })).json(); } catch (e) {} }
  async function wifiScan() {
    wf.msg = 'Looking for networks…'; wf.nets = []; drawWifi();
    try {
      const r = await (await fetch('/api/wifi/scan', { cache: 'no-store' })).json();
      wf.nets = r.networks || []; wf.msg = r.error || (wf.nets.length ? '' : 'No networks found. Tap Rescan.');
    } catch (e) { wf.msg = 'Scan failed. Tap Rescan.'; }
    if (wifiOpen() && wf.view === 'list') drawWifi();
  }
  async function openWifi() {
    wf = { ...wf, view: 'list', text: '', show: false, layer: 'lower' };
    await wifiStatus(); drawWifi(); wifi.classList.add('show'); wifiScan();
  }
  function closeWifi() { wifi.classList.remove('show'); menuClosedAt = performance.now(); }
  async function startConnect(psk) {
    wf.view = 'status'; wf.st.attempt = { state: 'connecting' }; drawWifi();
    try {
      const r = await post('/api/wifi/connect', { ssid: wf.ssid, psk });
      if (!r.ok) { const j = await r.json(); wf.st.attempt = { state: 'failed', error: j.error }; drawWifi(); return; }
    } catch (e) { wf.st.attempt = { state: 'failed', error: 'Lost contact with the scoreboard.' }; drawWifi(); return; }
    const t0 = Date.now();
    const tick = async () => {
      await wifiStatus();
      const s2 = (wf.st.attempt || {}).state;
      if (s2 === 'connecting' && Date.now() - t0 < 150000) { drawWifi(); setTimeout(tick, 1500); return; }
      drawWifi();
    };
    setTimeout(tick, 1500);
  }
  onTap(wifi, b => {
    const w = b.dataset.w, key = b.dataset.key;
    if (key) {
      if (key === 'SHIFT') wf.layer = wf.layer === 'upper' ? 'lower' : 'upper';
      else if (key === 'SYM') wf.layer = 'sym';
      else if (key === 'ABC') wf.layer = 'lower';
      else if (key === 'BKSP') wf.text = wf.text.slice(0, -1);
      else if (key === 'SPACE') wf.text += ' ';
      else { wf.text += key; if (wf.layer === 'upper') wf.layer = 'lower'; }
      if (wf.text.length > 63) wf.text = wf.text.slice(0, 63);
      return drawWifi();
    }
    if (w === 'close') return closeWifi();
    if (w === 'scan') return wifiScan();
    if (w === 'list') { wf.view = 'list'; drawWifi(); return wifiScan(); }
    if (w === 'pick') {
      wf.ssid = b.dataset.ssid;
      if (b.dataset.secure === '0') return startConnect('');
      wf = { ...wf, view: 'type', step: 'psk', text: '', show: false, layer: 'lower' }; return drawWifi();
    }
    if (w === 'other') { wf = { ...wf, view: 'type', step: 'ssid', text: '', layer: 'lower' }; return drawWifi(); }
    if (w === 'showpw') { wf.show = !wf.show; return drawWifi(); }
    if (w === 'back') { wf.view = 'list'; return drawWifi(); }
    if (w === 'retry') { wf = { ...wf, view: 'type', step: 'psk', text: '' }; return drawWifi(); }
    if (w === 'go') {
      if (wf.step === 'ssid') {
        if (!wf.text.trim()) return;
        wf.ssid = wf.text.trim(); wf = { ...wf, step: 'psk', text: '', layer: 'lower' }; return drawWifi();
      }
      if (wf.text && wf.text.length < 8) { wf.msg = ''; return; }
      return startConnect(wf.text);
    }
  });

  // "No Wi-Fi" screen: shows when the board has been offline for a minute
  const offline = document.createElement('div');
  offline.id = 'offline';
  offline.innerHTML = `<div class="ot">NO WI-FI</div><div class="om">The scoreboard lost its Wi-Fi connection.</div>
    <button data-o="setup">Set up Wi-Fi</button><div class="oh">Scores will come back on their own once it reconnects.</div>`;
  board.appendChild(offline);
  onTap(offline, b => { if (b.dataset.o === 'setup') openWifi(); });
  function offlineScreen(w) { offline.classList.toggle('show', !!(w.available && w.offline) && !wifiOpen()); }

  // tap recorder (troubleshooting): every input event is sent to /api/touchlog, readable from any browser
  let tlog = [];
  const describe = el => el ? (el.id ? '#' + el.id : '') + (el.tagName || '') + (el.dataset && (el.dataset.k || el.dataset.act) ? '[' + (el.dataset.k || el.dataset.act) + '=' + (el.dataset.v || '') + ']' : '') : '-';
  ['pointerdown', 'pointerup', 'pointercancel', 'click', 'touchstart', 'touchend', 'touchcancel', 'contextmenu', 'mousedown', 'mouseup'].forEach(t =>
    addEventListener(t, ev => {
      tlog.push(`${t} ${ev.pointerType || ''} x=${Math.round(ev.clientX ?? (ev.changedTouches && ev.changedTouches[0] ? ev.changedTouches[0].clientX : -1))} ` +
        `y=${Math.round(ev.clientY ?? (ev.changedTouches && ev.changedTouches[0] ? ev.changedTouches[0].clientY : -1))} on=${describe(ev.target)} menu=${menuOpen() ? 'open' : 'closed'} armed=${menuArmed}`);
    }, true));
  setInterval(() => { if (tlog.length) { const b = tlog; tlog = []; post('/api/touchlog', b).catch(() => {}); } }, 1000);

  // hide the mouse pointer unless a real mouse is moving (touch never shows it)
  let curTimer;
  document.documentElement.classList.add('nocur');
  addEventListener('pointermove', ev => {
    if (ev.pointerType !== 'mouse') return;
    document.documentElement.classList.remove('nocur');
    clearTimeout(curTimer);
    curTimer = setTimeout(() => document.documentElement.classList.add('nocur'), 3000);
  });
  addEventListener('pointerdown', ev => { if (ev.pointerType !== 'mouse') document.documentElement.classList.add('nocur'); });

  addEventListener('keydown', ev => {
    if (ev.key === 'm') return menuOpen() ? closeMenu() : openMenu();
    if (ev.key === 'Escape' && menuOpen()) return closeMenu();
    const ctl = { ArrowRight: 'next', ArrowLeft: 'prev', a: 'auto', Escape: 'auto' }[ev.key];
    if (ctl) { post('/api/control', { action: ctl }).then(() => schedule(30)); return; }
    const test = { t: 'touchdown', f: 'field_goal', d: 'first_down', r: 'red_zone', i: 'turnover', s: 'safety', x: 'extra_point', g: 'final' }[ev.key];
    if (test) post('/api/test', { kind: test }).then(() => schedule(30));
  });

  layout();
  poll();
})();
