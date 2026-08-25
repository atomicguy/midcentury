#!/usr/bin/env python3
"""Derive 'Midcentury Light' from Adam Schuster's Midcentury (MIT) VS Code theme.

The dark theme uses a 16-color palette: a brown→cream neutral ramp (0-7) and
eight accents (8-F).  The light theme inverts the neutral ramp and keeps the
accents as fills, darkening them only where they are used as text so every
foreground reaches WCAG AA (4.5:1) on the cream editor background.
"""
import colorsys, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'themes', 'Midcentury-color-theme.json')
OUT = os.path.join(HERE, '..', 'themes', 'Midcentury-light-color-theme.json')

# ---- helpers ----------------------------------------------------------------
def load_jsonc(path):
    s = open(path).read()
    s = re.sub(r'//[^\n]*', '', s)          # no '//' occurs inside strings in this file
    s = re.sub(r',(\s*[}\]])', r'\1', s)     # trailing commas
    return json.loads(s)

def rgb(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

def hexs(r, g, b):
    return '#%02X%02X%02X' % tuple(int(round(max(0, min(1, v)) * 255)) for v in (r, g, b))

def lum(h):
    def ch(c): return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h); return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

def contrast(a, b):
    la, lb = lum(a), lum(b); la, lb = max(la, lb), min(la, lb)
    return (la + 0.05) / (lb + 0.05)

def darken_to(h, bg, target=4.5):
    """Lower HSL lightness (hue & saturation fixed) until contrast >= target."""
    hh, l, s = colorsys.rgb_to_hls(*rgb(h))
    while contrast(hexs(*colorsys.hls_to_rgb(hh, l, s)), bg) < target and l > 0.02:
        l -= 0.01
    return hexs(*colorsys.hls_to_rgb(hh, l, s))

def split(v):
    """'#RRGGBBAA' -> ('#RRGGBB', 'AA'); handles #RGB."""
    v = v.strip()
    if len(v) == 4: v = '#' + ''.join(c * 2 for c in v[1:])
    return v[:7].upper(), v[7:]

# ---- the palette --------------------------------------------------------------
BG = '#FDFBEC'   # 7 — becomes the editor background

# neutral ramp: dark value -> (as background, as foreground)
NEUTRAL = {
    '#250F0E': ('#F4EAD3', '#1A0908'),   # 0' darkest chrome (sidebar, tab bar, title bar)
    '#321513': ('#FDFBEC', '#321513'),   # 0  editor bg  -> cream ; as text stays deep brown
    '#312513': ('#F4EAD3', '#1A0908'),   # (typo in source for titleBar.inactive) treat as 0'
    '#4E322C': ('#F5E9CE', '#3F2620'),   # 1  line highlight / active tab / menus
    '#6B5046': ('#EAD8B8', '#4E322C'),   # 2  selection / hover / widgets
    '#A48B79': ('#DEC7AC', '#7D6252'),   # 3  muted (line numbers, comments, inactive tabs)
    '#DEC7AC': ('#D4B894', '#6B5046'),   # 4  icons, active line number
    '#FBE5C6': ('#F5E9CE', '#321513'),   # 5  main foreground -> deep brown
    '#FCF3DE': ('#F5E9CE', '#250F0E'),   # 6
    '#FDFBEC': ('#EAD8B8', '#250F0E'),   # 7  brightest text -> darkest text
}
ACCENTS = ['#DB72AE', '#DB7D33', '#D55D5C', '#589ACE', '#43AC75', '#308E95', '#63CCE3', '#6F4EBC']
ACCENT_FG = {a: darken_to(a, BG) for a in ACCENTS}     # text-safe versions
ACCENT_FG['#63CCE3'] = darken_to('#4DB8D0', BG)          # cyan: start a touch deeper so it stays cyan, not navy

def is_fg_key(key):
    k = key.lower()
    return ('foreground' in k or k.endswith('.stroke') or k in ('foreground',))

def map_color(value, as_fg):
    base, a = split(value)
    if base in NEUTRAL:
        return NEUTRAL[base][1 if as_fg else 0] + a
    if base in ACCENT_FG:
        return (ACCENT_FG[base] if as_fg else base) + a
    if base == '#FF00FF':   # author's '#f0f' placeholders
        return ('#7D6252' if as_fg else '#EAD8B8') + a
    if base == '#324E2C':   # one-off (sideBar.dropBackground)
        return '#DDE7D4' + a
    if base == '#000000':
        return base + a
    raise ValueError(f'unmapped color {value}')

# ---- workbench colors ----------------------------------------------------------
src = load_jsonc(SRC)
colors = {k: map_color(v, is_fg_key(k)) for k, v in src['colors'].items()}

# text that sits ON an accent fill must stay cream, and a few semantics that
# don't survive a naive inversion
colors.update({
    'statusBar.foreground': '#FDFBEC', 'statusBar.debuggingForeground': '#FDFBEC',
    'statusBar.noFolderForeground': '#FDFBEC', 'statusBar.noFolderBackground': '#43AC75',
    'statusBarItem.prominentForeground': '#FDFBEC', 'statusBarItem.remoteForeground': '#FDFBEC',
    'statusBarItem.hoverBackground': '#FFFFFF30', 'statusBarItem.activeBackground': '#FFFFFF50',
    'activityBarBadge.foreground': '#FDFBEC',
    'badge.background': '#308E95', 'badge.foreground': '#FDFBEC',
    'button.background': '#308E95', 'button.foreground': '#FDFBEC', 'button.hoverBackground': '#43AC75',
    'extensionButton.prominentForeground': '#FDFBEC', 'extensionButton.prominentHoverBackground': '#308E95',
    'extensionBadge.remoteForeground': '#FDFBEC',
    'inputValidation.errorForeground': '#FDFBEC', 'inputValidation.infoForeground': '#FDFBEC',
    'inputValidation.warningForeground': '#FDFBEC',
    'list.highlightForeground': ACCENT_FG['#308E95'],
    'list.hoverBackground': '#F0E2C6',
    'list.dropBackground': '#EAD8B880',
    'activityBar.dropBackground': '#EAD8B880',
    'editorSuggestWidget.highlightForeground': ACCENT_FG['#308E95'],
    'editorWidget.background': '#F5E9CE',
    'notifications.background': '#F5E9CE',
    'menu.separatorBackground': '#DEC7AC',
    'scrollbar.shadow': '#4E322C40',
    'widget.shadow': '#4E322C40',
    'progressBar.background': '#308E95',
    'editorOverviewRuler.bracketMatchForeground': '#7D6252',
    'editorOverviewRuler.wordHighlightForeground': '#6B50466F',
    'editor.selectionBackground': '#DEC7AC',
    'editor.inactiveSelectionBackground': '#EAD8B8',
    'editor.selectionHighlightBackground': '#EAD8B8',
    'editor.wordHighlightBackground': '#DEC7AC6F', 'editor.wordHighlightStrongBackground': '#D4B8946F',
    'editor.lineHighlightBackground': '#F5E9CE',
    'editorIndentGuide.background': '#EAD8B8', 'editorIndentGuide.activeBackground': '#DEC7AC',
    'editorBracketMatch.background': '#DEC7AC',
    'tab.activeBackground': '#FDFBEC', 'tab.inactiveBackground': '#F4EAD3',
    'tab.unfocusedActiveBackground': '#F5E9CE', 'tab.hoverBackground': '#F5E9CE',
    'tab.unfocusedHoverBackground': '#F5E9CE',
    'tab.activeForeground': '#321513', 'tab.inactiveForeground': '#7D6252',
    'tab.unfocusedActiveForeground': '#6B5046',
    'editorGroupHeader.noTabsBackground': '#F4EAD3',
    'breadcrumb.background': '#FDFBEC',
    'sideBarSectionHeader.background': '#EAD8B8',
    'titleBar.inactiveBackground': '#F4EAD3',
    'terminal.ansiBlack': '#321513', 'terminal.ansiWhite': '#DEC7AC',
    'terminal.ansiBrightBlack': '#7D6252', 'terminal.ansiBrightWhite': '#FDFBEC',
    'terminal.ansiRed': ACCENT_FG['#DB72AE'], 'terminal.ansiGreen': ACCENT_FG['#589ACE'],
    'terminal.ansiYellow': ACCENT_FG['#D55D5C'], 'terminal.ansiBlue': ACCENT_FG['#308E95'],
    'terminal.ansiMagenta': ACCENT_FG['#63CCE3'], 'terminal.ansiCyan': ACCENT_FG['#43AC75'],
    'terminal.ansiBrightRed': '#DB72AE', 'terminal.ansiBrightGreen': '#589ACE',
    'terminal.ansiBrightYellow': '#D55D5C', 'terminal.ansiBrightBlue': '#308E95',
    'terminal.ansiBrightMagenta': '#63CCE3', 'terminal.ansiBrightCyan': '#43AC75',
    'debugIcon.breakpointDisabledForeground': '#DEC7AC',
    'editorGutter.commentRangeForeground': '#DEC7AC',
    'editorCodeLens.foreground': '#7D6252',
    'symbolIcon.colorForeground': ACCENT_FG['#DB7D33'],
})
colors.pop('editorGroup.background', None)   # removed from VS Code in 1.24

# ---- token colors ----------------------------------------------------------------
tokens = []
for rule in src['tokenColors']:
    st = dict(rule['settings'])
    if 'foreground' in st:
        base, a = split(st['foreground'])
        st['foreground'] = '#4E322C50' if base == '#000000' else map_color(st['foreground'], True)
    tokens.append({**rule, 'settings': st})

theme = {'name': 'Midcentury Light', 'type': 'light', 'colors': colors, 'tokenColors': tokens}
with open(OUT, 'w') as f:
    json.dump(theme, f, indent=4); f.write('\n')

# ---- report ----------------------------------------------------------------------
print('accent -> text-safe on', BG)
for a in ACCENTS:
    print(f'  {a}  ->  {ACCENT_FG[a]}   {contrast(a, BG):.1f}:1 -> {contrast(ACCENT_FG[a], BG):.1f}:1')
print('neutral fg contrasts on editor bg:')
for d, (b, fg) in NEUTRAL.items():
    print(f'  {d} -> bg {b} / fg {fg}  ({contrast(fg, BG):.1f}:1)')
low = [(r['name'], r['settings']['foreground']) for r in tokens
       if 'foreground' in r['settings'] and len(r['settings']['foreground']) == 7
       and contrast(r['settings']['foreground'], BG) < 4.5]
print('token rules under 4.5:1:', low or 'none')
print(f'wrote {os.path.relpath(OUT)}: {len(colors)} colors, {len(tokens)} token rules')
