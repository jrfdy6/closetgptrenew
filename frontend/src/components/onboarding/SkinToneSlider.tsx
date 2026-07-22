interface SkinToneSliderProps {
  value: number;
  onValueChange: (value: number) => void;
}

const SKIN_TONE_GRADIENT =
  'linear-gradient(to right, #FEF3C7, #FDE68A, #FCD34D, #F59E0B, #D97706, #B45309, #92400E, #78350F, #451A03, #1F2937)';

function clampSkinTone(value: number): number {
  if (!Number.isFinite(value)) return 50;
  return Math.min(100, Math.max(0, Math.round(value)));
}

export function SkinToneSlider({ value, onValueChange }: SkinToneSliderProps) {
  const normalizedValue = clampSkinTone(value);
  const swatchColor = `hsl(${Math.max(0, 30 - normalizedValue * 0.3)}, ${Math.max(
    20,
    60 - normalizedValue * 0.4
  )}%, ${Math.max(20, 80 - normalizedValue * 0.6)}%)`;

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border-2 border-gray-200 dark:border-gray-700">
        <div className="space-y-4">
          <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400" aria-hidden="true">
            <span>Lightest</span>
            <span>Darkest</span>
          </div>
          <label htmlFor="skin-tone-depth" className="sr-only">
            Skin tone depth
          </label>
          <input
            id="skin-tone-depth"
            name="skinTone"
            type="range"
            min={0}
            max={100}
            step={1}
            value={normalizedValue}
            aria-describedby="skin-tone-depth-description"
            aria-valuetext={`${normalizedValue} percent skin tone depth`}
            className="w-full h-8 rounded-lg appearance-none cursor-pointer"
            style={{ background: SKIN_TONE_GRADIENT }}
            onInput={(event) => onValueChange(clampSkinTone(Number(event.currentTarget.value)))}
          />
          <div className="text-center">
            <div
              aria-hidden="true"
              className="w-16 h-16 rounded-full border-4 border-gray-300 dark:border-gray-600 mx-auto mb-2"
              style={{ backgroundColor: swatchColor }}
            />
            <p id="skin-tone-depth-description" className="text-sm text-gray-600 dark:text-gray-400">
              Skin tone depth: {normalizedValue}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
