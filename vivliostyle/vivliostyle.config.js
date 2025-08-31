module.exports = {
  title: "モダンテンプレート集",
  author: "デザイン研究家",
  language: "ja",
  size: "A4",
  entry: [
    "sample/templates/modern/title/modern-title-page/index.html",
    "sample/templates/modern/single/modern-minimal-single/index.html",
    "sample/templates/modern/spread/modern-balanced-spread/index.html"
  ],
  output: [
    "output/modern-templates.pdf"
  ],
  workspaceDir: ".",
  toc: true,
  tocTitle: "目次",
  print: true,
  pressReady: false,
  html: {
    toc: true,
    tocTitle: "目次"
  }
};
