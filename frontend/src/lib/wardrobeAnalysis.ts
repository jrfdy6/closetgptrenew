import { getWardrobeItems } from './firebase/wardrobeService';

export async function analyzeWardrobeMetadata(userId: string) {
  const response = await getWardrobeItems(userId);
  const items = response.data || [];
  const totalItems = items.length;

  // Categorize items
  const categories = {
    tops: items.filter(item => ['shirt', 'blouse', 't-shirt', 'sweater', 'tank top'].includes(item.type)),
    bottoms: items.filter(item => ['pants', 'skirt', 'shorts', 'jeans'].includes(item.type)),
    shoes: items.filter(item => ['shoes', 'boots', 'sneakers', 'sandals'].includes(item.type)),
    layers: items.filter(item => ['jacket', 'coat', 'sweater', 'cardigan', 'blazer'].includes(item.type)),
    accessories: items.filter(item => ['hat', 'bag', 'belt', 'scarf', 'jewelry'].includes(item.type))
  };

  const categoryStats = {
    tops: {
      count: categories.tops.length,
      percentage: ((categories.tops.length / totalItems) * 100).toFixed(1) + '%',
      types: countByType(categories.tops)
    },
    bottoms: {
      count: categories.bottoms.length,
      percentage: ((categories.bottoms.length / totalItems) * 100).toFixed(1) + '%',
      types: countByType(categories.bottoms)
    },
    shoes: {
      count: categories.shoes.length,
      percentage: ((categories.shoes.length / totalItems) * 100).toFixed(1) + '%',
      types: countByType(categories.shoes)
    },
    layers: {
      count: categories.layers.length,
      percentage: ((categories.layers.length / totalItems) * 100).toFixed(1) + '%',
      types: countByType(categories.layers)
    },
    accessories: {
      count: categories.accessories.length,
      percentage: ((categories.accessories.length / totalItems) * 100).toFixed(1) + '%',
      types: countByType(categories.accessories)
    }
  };

  const basicFields = {
    name: calculatePercentage(items, item => !!item.name),
    type: calculatePercentage(items, item => !!item.type),
    color: calculatePercentage(items, item => !!item.color),
    season: calculatePercentage(items, item => !!item.season),
    imageUrl: calculatePercentage(items, item => !!item.imageUrl),
    tags: calculatePercentage(items, item => !!item.tags && item.tags.length > 0),
    style: calculatePercentage(items, item => !!item.style),
    occasion: calculatePercentage(items, item => !!item.occasion),
  };

  const metadataFields = {
    visualAttributes: {
      material: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.material),
      pattern: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.pattern),
      textureStyle: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.textureStyle),
      fabricWeight: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.fabricWeight),
      fit: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.fit),
      silhouette: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.silhouette),
      length: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.length),
      genderTarget: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.genderTarget),
      sleeveLength: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.sleeveLength),
      hangerPresent: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.hangerPresent),
      backgroundRemoved: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.backgroundRemoved),
      wearLayer: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.wearLayer),
      formalLevel: calculatePercentage(items, item => !!item.metadata?.visualAttributes?.formalLevel),
    },
    itemMetadata: {
      priceEstimate: calculatePercentage(items, item => !!item.metadata?.itemMetadata?.priceEstimate),
      careInstructions: calculatePercentage(items, item => !!item.metadata?.itemMetadata?.careInstructions),
      tags: calculatePercentage(items, item => !!item.metadata?.itemMetadata?.tags && item.metadata.itemMetadata.tags.length > 0),
    },
    colorAnalysis: {
      primaryColor: calculatePercentage(items, item => !!item.metadata?.colorAnalysis?.primaryColor),
      secondaryColor: calculatePercentage(items, item => !!item.metadata?.colorAnalysis?.secondaryColor),
      colorPalette: calculatePercentage(items, item => !!item.metadata?.colorAnalysis?.colorPalette && item.metadata.colorAnalysis.colorPalette.length > 0),
    },
  };

  return {
    totalItems,
    categoryStats,
    basicFields,
    metadataFields,
  };
}

function calculatePercentage(items: any[], condition: (item: any) => boolean): string {
  const validItems = items.filter(condition).length;
  const percentage = (validItems / items.length) * 100;
  return `${percentage.toFixed(1)}%`;
}

function countByType(items: any[]): { [key: string]: number } {
  return items.reduce((acc, item) => {
    acc[item.type] = (acc[item.type] || 0) + 1;
    return acc;
  }, {});
}

export function formatMetadataReport(report: any): string {
  let formattedReport = `Total Items: ${report.totalItems}\n\n`;

  // Add category statistics
  formattedReport += 'Wardrobe Categories:\n';
  formattedReport += '===================\n\n';

  Object.entries(report.categoryStats).forEach(([category, stats]: [string, any]) => {
    formattedReport += `${category.charAt(0).toUpperCase() + category.slice(1)}:\n`;
    formattedReport += `  Count: ${stats.count} (${stats.percentage} of total)\n`;
    formattedReport += '  Types:\n';
    Object.entries(stats.types).forEach(([type, count]: [string, any]) => {
      formattedReport += `    - ${type}: ${count}\n`;
    });
    formattedReport += '\n';
  });

  // Add basic fields
  formattedReport += 'Basic Fields Completion:\n';
  formattedReport += '======================\n\n';
  Object.entries(report.basicFields).forEach(([field, percentage]: [string, any]) => {
    formattedReport += `${field}: ${percentage}\n`;
  });
  formattedReport += '\n';

  // Add metadata fields
  formattedReport += 'Metadata Fields Completion:\n';
  formattedReport += '========================\n\n';
  Object.entries(report.metadataFields).forEach(([category, fields]: [string, any]) => {
    formattedReport += `${category}:\n`;
    Object.entries(fields).forEach(([field, percentage]: [string, any]) => {
      formattedReport += `  ${field}: ${percentage}\n`;
    });
    formattedReport += '\n';
  });

  return formattedReport;
} 