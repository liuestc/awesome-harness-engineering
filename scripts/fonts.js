/**
 * fonts.js
 * 用 file:// 路径引用系统本地字体，注入到 HTML <head>
 * 避免 base64 内存溢出，也避免 Google Fonts 网络超时
 */

const FONT_FACES = `
<style>
@font-face { font-family: 'Noto Sans SC'; font-weight: 300; src: url('file:///usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc'); }
@font-face { font-family: 'Noto Sans SC'; font-weight: 400; src: url('file:///usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf'); }
@font-face { font-family: 'Noto Sans SC'; font-weight: 700; src: url('file:///usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'); }
@font-face { font-family: 'Noto Sans SC'; font-weight: 900; src: url('file:///usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'); }
@font-face { font-family: 'Noto Serif SC'; font-weight: 400; src: url('file:///usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'); }
@font-face { font-family: 'Noto Serif SC'; font-weight: 600; src: url('file:///usr/share/fonts/opentype/noto/NotoSerifCJK-SemiBold.ttc'); }
@font-face { font-family: 'Noto Serif SC'; font-weight: 700; src: url('file:///usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'); }
@font-face { font-family: 'JetBrains Mono'; font-weight: 400; src: url('file:///usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf'); }
@font-face { font-family: 'JetBrains Mono'; font-weight: 700; src: url('file:///usr/share/fonts/truetype/noto/NotoSansMono-Bold.ttf'); }
@font-face { font-family: 'Orbitron'; font-weight: 400; src: url('file:///usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf'); }
@font-face { font-family: 'Orbitron'; font-weight: 700; src: url('file:///usr/share/fonts/truetype/noto/NotoSansMono-Bold.ttf'); }
@font-face { font-family: 'Orbitron'; font-weight: 900; src: url('file:///usr/share/fonts/truetype/noto/NotoSansMono-Bold.ttf'); }
@font-face { font-family: 'Playfair Display'; font-weight: 700; src: url('file:///usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'); }
@font-face { font-family: 'Playfair Display'; font-weight: 900; src: url('file:///usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'); }
</style>`;

function getFontFaceCSS() {
  return FONT_FACES;
}

module.exports = { getFontFaceCSS };
