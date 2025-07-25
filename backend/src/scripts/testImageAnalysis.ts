import { OpenAI } from "openai";
import { config } from "dotenv";
import path from "path";
import fs from "fs";
import type { OpenAIClothingAnalysis } from "../../../shared/types";

// Load environment variables
config();

console.log("Environment variables loaded:");
console.log("OPENAI_API_KEY exists:", !!process.env.OPENAI_API_KEY);
console.log("OPENAI_API_KEY length:", process.env.OPENAI_API_KEY?.length);

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function analyzeClothingImage(imagePath: string): Promise<OpenAIClothingAnalysis> {
  try {
    // Read the image file and convert to base64
    const imageBuffer = fs.readFileSync(imagePath);
    const base64Image = imageBuffer.toString('base64');
    const imageUrl = `data:image/jpeg;base64,${base64Image}`;

    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        {
          role: "user",
          content: [
            {
              type: "text",
              text: `Analyze this clothing item and provide the following information in JSON format:
              {
                "type": "One of: shirt, pants, dress, skirt, jacket, sweater, shoes, accessory, other",
                "subType": "More specific type (e.g., 't-shirt', 'jeans', 'sundress')",
                "dominantColors": [
                  {
                    "name": "Color name",
                    "hex": "Hex color code",
                    "rgb": [R, G, B]
                  }
                ],
                "matchingColors": [
                  {
                    "name": "Color name",
                    "hex": "Hex color code",
                    "rgb": [R, G, B]
                  }
                ],
                "style": ["Array of style tags like: Casual, Formal, Sporty, etc."],
                "brand": "Brand name if visible (optional)",
                "season": ["Array of applicable seasons: spring, summer, fall, winter"],
                "occasion": ["Array of occasions like: Casual, Formal, Business, etc."]
              }
              
              Focus on accuracy and be specific. Consider current fashion trends.`,
            },
            {
              type: "image_url",
              image_url: { url: imageUrl }
            },
          ],
        },
      ],
      max_tokens: 1000,
    });

    const content = response.choices[0].message.content;
    if (!content) throw new Error("No response from OpenAI");
    
    // Remove markdown formatting if present
    const jsonStr = content.replace(/^```json\n|\n```$/g, '');
    return JSON.parse(jsonStr) as OpenAIClothingAnalysis;
  } catch (error) {
    console.error("Error analyzing image:", error);
    throw error;
  }
}

async function main() {
  try {
    // Get the image path from command line arguments
    const imagePath = process.argv[2];
    if (!imagePath) {
      console.error("Please provide an image path as an argument");
      process.exit(1);
    }

    // Check if the file exists
    if (!fs.existsSync(imagePath)) {
      console.error(`File not found: ${imagePath}`);
      process.exit(1);
    }

    console.log(`Analyzing image: ${imagePath}`);
    const analysis = await analyzeClothingImage(imagePath);
    
    // Output the analysis in a formatted way
    console.log("\nAnalysis Results:");
    console.log(JSON.stringify(analysis, null, 2));
    
    // Save the analysis to a JSON file
    const outputPath = path.join(
      path.dirname(imagePath),
      `${path.basename(imagePath, path.extname(imagePath))}_analysis.json`
    );
    fs.writeFileSync(outputPath, JSON.stringify(analysis, null, 2));
    console.log(`\nAnalysis saved to: ${outputPath}`);

  } catch (error) {
    console.error("Error:", error);
    process.exit(1);
  }
}

main(); 