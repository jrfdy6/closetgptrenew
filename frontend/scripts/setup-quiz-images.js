const fs = require('fs');
const path = require('path');
const https = require('https');

const quizImages = [
  {
    name: 'business-classic.jpg',
    url: 'https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=800&q=80'
  },
  {
    name: 'street-style.jpg',
    url: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80'
  },
  {
    name: 'bohemian.jpg',
    url: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80'
  }
];

const downloadImage = (url, filename) => {
  return new Promise((resolve, reject) => {
    https.get(url, (response) => {
      if (response.statusCode === 200) {
        const fileStream = fs.createWriteStream(filename);
        response.pipe(fileStream);
        fileStream.on('finish', () => {
          fileStream.close();
          resolve();
        });
      } else {
        reject(new Error(`Failed to download ${url}`));
      }
    }).on('error', reject);
  });
};

const setupQuizImages = async () => {
  const imagesDir = path.join(__dirname, '../public/quiz-images');
  
  // Create directory if it doesn't exist
  if (!fs.existsSync(imagesDir)) {
    fs.mkdirSync(imagesDir, { recursive: true });
  }

  // Download each image
  for (const image of quizImages) {
    const filename = path.join(imagesDir, image.name);
    console.log(`Downloading ${image.name}...`);
    try {
      await downloadImage(image.url, filename);
      console.log(`Successfully downloaded ${image.name}`);
    } catch (error) {
      console.error(`Error downloading ${image.name}:`, error);
    }
  }
};

setupQuizImages().catch(console.error); 