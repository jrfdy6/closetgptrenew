import React from 'react';
import { PhotoAnalysis } from '@/types/photo-analysis';

interface PhotoAnalysisResultsProps {
  analysis: PhotoAnalysis;
  type: 'fullBody' | 'outfit';
}

export const PhotoAnalysisResults: React.FC<PhotoAnalysisResultsProps> = ({ analysis, type }) => {
  return (
    <div className="space-y-6 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold text-gray-800">
        {type === 'fullBody' ? 'Body Analysis' : 'Outfit Analysis'}
      </h2>

      {type === 'fullBody' && analysis.bodyMeasurements && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-700">Body Measurements</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Height</p>
              <p className="font-medium">{analysis.bodyMeasurements.height} cm</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Body Type</p>
              <p className="font-medium capitalize">{analysis.bodyMeasurements.bodyType}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Shoulder Width</p>
              <p className="font-medium">{analysis.bodyMeasurements.shoulderWidth} cm</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Waist Width</p>
              <p className="font-medium">{analysis.bodyMeasurements.waistWidth} cm</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Hip Width</p>
              <p className="font-medium">{analysis.bodyMeasurements.hipWidth} cm</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Inseam</p>
              <p className="font-medium">{analysis.bodyMeasurements.inseam} cm</p>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-700">Color Analysis</h3>
        <div>
          <p className="text-sm text-gray-500 mb-2">Primary Colors</p>
          <div className="flex gap-2">
            {analysis.colorAnalysis.primaryColors.map((color, index) => (
              <div
                key={index}
                className="w-8 h-8 rounded-full border border-gray-200"
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
        </div>
        <div>
          <p className="text-sm text-gray-500 mb-2">Secondary Colors</p>
          <div className="flex gap-2">
            {analysis.colorAnalysis.secondaryColors.map((color, index) => (
              <div
                key={index}
                className="w-8 h-8 rounded-full border border-gray-200"
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
        </div>
        {type === 'fullBody' && (
          <div>
            <p className="text-sm text-gray-500 mb-2">Skin Tone</p>
            <div className="flex items-center gap-4">
              <div
                className="w-8 h-8 rounded-full border border-gray-200"
                style={{ backgroundColor: analysis.colorAnalysis.skinTone.shade }}
              />
              <div>
                <p className="font-medium capitalize">{analysis.colorAnalysis.skinTone.undertone}</p>
                <p className="text-sm text-gray-500">{analysis.colorAnalysis.skinTone.shade}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {type === 'outfit' && analysis.outfitAnalysis && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-700">Outfit Details</h3>
          <div>
            <p className="text-sm text-gray-500 mb-2">Garments</p>
            <div className="space-y-2">
              {analysis.outfitAnalysis.garments.map((garment, index) => (
                <div key={index} className="flex items-center gap-4">
                  <div
                    className="w-6 h-6 rounded-full border border-gray-200"
                    style={{ backgroundColor: garment.color }}
                  />
                  <div>
                    <p className="font-medium capitalize">{garment.type}</p>
                    <p className="text-sm text-gray-500 capitalize">{garment.style.join(', ')}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-2">Overall Style</p>
            <div className="flex flex-wrap gap-2">
              {analysis.outfitAnalysis.overallStyle.map((style, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm capitalize"
                >
                  {style}
                </span>
              ))}
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-2">Formality Level</p>
            <p className="font-medium capitalize">{analysis.outfitAnalysis.formality}</p>
          </div>
        </div>
      )}

      <div className="pt-4 border-t border-gray-200">
        <p className="text-sm text-gray-500">Analysis Confidence</p>
        <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
          <div
            className="bg-blue-600 h-2.5 rounded-full"
            style={{ width: `${analysis.confidence * 100}%` }}
          />
        </div>
        <p className="text-sm text-gray-500 mt-1">
          {Math.round(analysis.confidence * 100)}% confidence
        </p>
      </div>
    </div>
  );
}; 