// scripts/generate-sitemap.js
const path = require('path');
const fs = require('fs-extra');
const { SitemapStream, streamToPromise } = require('sitemap');

// 1) Load your router file and grab the routes array
const { routes } = require('@/src/router/index.js');

// 2) Define your hostname
const hostname = 'https://sitchat.ai';

// 3) Filter out dynamic routes (those with “:” in the path)
const staticRoutes = routes
  .map(r => r.path)
  .filter(p => !p.includes(':'));

// 4) Create the sitemap
async function buildSitemap() {
  // ensure dist folder exists
  const distPath = path.resolve(__dirname, '@/dist');
  await fs.ensureDir(distPath);

  const sitemapStream = new SitemapStream({ hostname });
  const writeStream = fs.createWriteStream(path.join(distPath, 'sitemap.xml'));
  sitemapStream.pipe(writeStream);

  staticRoutes.forEach(url => {
    sitemapStream.write({
      url,
      changefreq: 'daily',
      priority: url === '/' ? 1.0 : 0.8,
    });
  });
  sitemapStream.end();

  await streamToPromise(writeStream);
  console.log(`📄  sitemap.xml created with ${staticRoutes.length} entries.`);
}

buildSitemap().catch(err => {
  console.error(err);
  process.exit(1);
});