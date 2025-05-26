#!/usr/bin/env node
import fs from 'fs-extra';
import path from 'path';
import { SitemapStream, streamToPromise } from 'sitemap';

async function buildSitemap() {
  // 1) Read your router file as plain text
  const routerFile = path.resolve('src/router/index.js');
  const content = await fs.readFile(routerFile, 'utf-8');

  // 2) Extract all `path: '/something'` values
  const pathRegex = /path:\s*['"`]([^'"`]+)['"`]/g;
  const allPaths = Array.from(content.matchAll(pathRegex), m => m[1]);

  // 3) De-duplicate and filter out dynamic routes (those containing ':')
  const staticRoutes = [...new Set(allPaths)].filter(p => !p.includes(':'));

  // 4) Ensure your dist folder exists
  const distDir = path.resolve('dist');
  await fs.ensureDir(distDir);

  // 5) Create & write sitemap.xml
  const sitemapPath = path.join(distDir, 'sitemap.xml');
  const writeStream = fs.createWriteStream(sitemapPath);
  const smStream = new SitemapStream({ hostname: 'https://sitchat.ai' });

  // Pipe the sitemap data into the file
  smStream.pipe(writeStream);

  // Write each URL entry
  staticRoutes.forEach(url => {
    smStream.write({
      url,
      changefreq: 'daily',
      priority: url === '/' ? 1.0 : 0.8,
    });
  });

  // Close the stream to flush everything
  smStream.end();

  // **Here’s the fix**: wait on the SitemapStream, not the write stream
  await streamToPromise(smStream);

  console.log(`✔️  Generated sitemap.xml with ${staticRoutes.length} URLs.`);
}

buildSitemap().catch(err => {
  console.error(err);
  process.exit(1);
});