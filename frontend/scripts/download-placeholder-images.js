const fs = require('fs');
const path = require('path');
const https = require('https');

const bodyTypes = [
  'athletic',
  'curvy',
  'rectangular',
  'hourglass',
  'pear',
  'apple',
  'inverted',
];

const styles = [
  'minimal',
  'gorpcore',
  'boho',
  'street',
  'oldmoney',
  'cleangirl',
  'korean',
  'y2k',
  'coastal',
  'darkacad',
];

const downloadImage = (url, filepath) => {
  return new Promise((resolve, reject) => {
    https.get(url, (response) => {
      if (response.statusCode === 200) {
        const writeStream = fs.createWriteStream(filepath);
        response.pipe(writeStream);
        writeStream.on('finish', () => {
          writeStream.close();
          resolve();
        });
      } else {
        reject(new Error(`Failed to download ${url}`));
      }
    }).on('error', reject);
  });
};

const createDirectories = () => {
  const dirs = [
    'public/images/body-types',
    'public/images/styles',
  ];

  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
};

const downloadPlaceholderImages = async () => {
  createDirectories();

  // Download body type images
  for (const type of bodyTypes) {
    const url = `https://picsum.photos/400/600?random=${type}`;
    const filepath = path.join('public/images/body-types', `${type}.png`);
    await downloadImage(url, filepath);
    console.log(`Downloaded ${type} body type image`);
  }

  // Download style images
  for (const style of styles) {
    const url = `https://picsum.photos/800/600?random=${style}`;
    const filepath = path.join('public/images/styles', `${style}.jpg`);
    await downloadImage(url, filepath);
    console.log(`Downloaded ${style} style image`);
  }
};

downloadPlaceholderImages().catch(console.error); 