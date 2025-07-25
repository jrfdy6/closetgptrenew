"use client";

import { useState } from "react";
import Image from "next/image";
import { useStorage } from "@/lib/hooks/useStorage";
import { generateAvatarUrl, HAIR_STYLES, HAIR_COLORS } from "@/lib/utils/avatar";

interface AvatarSelectorProps {
  currentAvatar: string | null;
  onAvatarChange: (url: string) => void;
  initialGender?: "male" | "female";
  onComplete?: () => void;
}

type SkinTone = "light" | "medium-light" | "medium" | "medium-dark" | "dark" | "deep";

// Skin tone options with their corresponding color codes
const SKIN_TONES: { id: string; label: string; value: SkinTone; color: string }[] = [
  { id: "tone1", label: "Light", value: "light", color: "#FFE0BD" },
  { id: "tone2", label: "Medium Light", value: "medium-light", color: "#E6C7A9" },
  { id: "tone3", label: "Medium", value: "medium", color: "#D4B483" },
  { id: "tone4", label: "Medium Dark", value: "medium-dark", color: "#B38B6D" },
  { id: "tone5", label: "Dark", value: "dark", color: "#8B5A2B" },
  { id: "tone6", label: "Deep", value: "deep", color: "#5C4033" },
];

const FEMALE_AVATARS = [
  { id: "female1", type: "hourglass", label: "Hourglass" },
  { id: "female2", type: "pear", label: "Pear" },
  { id: "female3", type: "apple", label: "Apple" },
  { id: "female4", type: "rectangle", label: "Rectangle" },
  { id: "female5", type: "inverted-triangle", label: "Inverted Triangle" },
  { id: "female6", type: "petite", label: "Petite" },
  { id: "female7", type: "tall", label: "Tall" },
  { id: "female8", type: "plus-curvy", label: "Plus Size Curvy" },
  { id: "female9", type: "lean-column", label: "Lean Column" },
];

const MALE_AVATARS = [
  { id: "male1", type: "rectangle", label: "Rectangle" },
  { id: "male2", type: "triangle", label: "Triangle" },
  { id: "male3", type: "inverted-triangle", label: "Inverted Triangle" },
  { id: "male4", type: "oval", label: "Oval" },
  { id: "male5", type: "trapezoid", label: "Trapezoid" },
  { id: "male6", type: "slim", label: "Slim" },
  { id: "male7", type: "stocky", label: "Stocky" },
  { id: "male8", type: "tall", label: "Tall" },
  { id: "male9", type: "short", label: "Short" },
];

export default function AvatarSelector({ currentAvatar, onAvatarChange, initialGender, onComplete }: AvatarSelectorProps) {
  const [selectedGender, setSelectedGender] = useState<"female" | "male">(initialGender || "female");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedTone, setSelectedTone] = useState<SkinTone>("light");
  const [selectedHairStyle, setSelectedHairStyle] = useState<string>(
    HAIR_STYLES[initialGender || "female"][0].value
  );
  const [selectedHairColor, setSelectedHairColor] = useState<string>(
    HAIR_COLORS[1].value
  );
  const [preview, setPreview] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const { uploadFile, uploading, error } = useStorage();
  const [imageError, setImageError] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      const path = `avatars/${selectedGender}/${selectedTone}/${Date.now()}_${file.name}`;
      const downloadURL = await uploadFile(file, path);
      onAvatarChange(downloadURL);
      setFile(null);
      setPreview("");
    } catch (err) {
      console.error("Error uploading avatar:", err);
    }
  };

  const currentAvatars = selectedGender === "female" ? FEMALE_AVATARS : MALE_AVATARS;
  const filteredAvatars = selectedType === "all"
    ? currentAvatars
    : currentAvatars.filter(avatar => avatar.type === selectedType);

  const bodyTypeOptions = selectedGender === "female"
    ? [
        { value: "all", label: "All Body Types" },
        { value: "hourglass", label: "Hourglass" },
        { value: "pear", label: "Pear" },
        { value: "apple", label: "Apple" },
        { value: "rectangle", label: "Rectangle" },
        { value: "inverted-triangle", label: "Inverted Triangle" },
        { value: "petite", label: "Petite" },
        { value: "tall", label: "Tall" },
        { value: "plus-curvy", label: "Plus Size Curvy" },
        { value: "lean-column", label: "Lean Column" },
      ]
    : [
        { value: "all", label: "All Body Types" },
        { value: "rectangle", label: "Rectangle" },
        { value: "triangle", label: "Triangle" },
        { value: "inverted-triangle", label: "Inverted Triangle" },
        { value: "oval", label: "Oval" },
        { value: "trapezoid", label: "Trapezoid" },
        { value: "slim", label: "Slim" },
        { value: "stocky", label: "Stocky" },
        { value: "tall", label: "Tall" },
        { value: "short", label: "Short" },
      ];

  const getAvatarUrl = (avatar: typeof FEMALE_AVATARS[0]) => {
    return generateAvatarUrl({
      gender: selectedGender,
      bodyType: avatar.type,
      skinTone: selectedTone,
      hairStyle: selectedHairStyle,
      hairColor: selectedHairColor,
    });
  };

  // Update hair style when gender changes
  const handleGenderChange = (gender: "female" | "male") => {
    setSelectedGender(gender);
    setSelectedHairStyle(HAIR_STYLES[gender][0].value);
    // Generate a new avatar URL with the updated gender
    if (currentAvatar) {
      const url = generateAvatarUrl({
        gender,
        bodyType: selectedType === "all" ? (gender === "female" ? "hourglass" : "rectangle") : selectedType,
        skinTone: selectedTone,
        hairStyle: HAIR_STYLES[gender][0].value,
        hairColor: selectedHairColor,
      });
      onAvatarChange(url);
    }
  };

  const handleAvatarSelect = (avatar: typeof FEMALE_AVATARS[0]) => {
    const url = getAvatarUrl(avatar);
    onAvatarChange(url);
    setShowPreview(true);
  };

  const handleImageError = () => {
    setImageError(true);
    console.error("Failed to load avatar image");
    // Retry loading with a different seed and simplified parameters
    if (currentAvatar) {
      const url = generateAvatarUrl({
        gender: selectedGender,
        bodyType: selectedType === "all" ? (selectedGender === "female" ? "hourglass" : "rectangle") : selectedType,
        skinTone: selectedTone,
        hairStyle: selectedHairStyle,
        hairColor: selectedHairColor,
        seed: `${Date.now()}-${Math.random()}`, // Add a unique seed
      });
      onAvatarChange(url);
    }
  };

  const handleContinue = () => {
    if (currentAvatar) {
      onComplete?.();
    }
  };

  return (
    <div className="space-y-6">
      {showPreview && currentAvatar && (
        <div className="relative w-48 h-48 mx-auto mb-4">
          <Image
            src={currentAvatar}
            alt="Selected Avatar"
            fill
            className="object-contain"
            sizes="(max-width: 768px) 100vw, 12rem"
            onError={handleImageError}
            unoptimized
            priority
            loading="eager"
          />
          <button 
            onClick={() => setShowPreview(false)}
            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center"
          >
            ×
          </button>
        </div>
      )}

      <div className="flex gap-4 justify-center">
        <button
          onClick={() => handleGenderChange("female")}
          className={`px-4 py-2 rounded ${
            selectedGender === "female" 
              ? "bg-blue-500 text-white" 
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Female
        </button>
        <button
          onClick={() => handleGenderChange("male")}
          className={`px-4 py-2 rounded ${
            selectedGender === "male" 
              ? "bg-blue-500 text-white" 
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Male
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Body Type</label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="w-full p-2 border rounded"
          >
            {bodyTypeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Skin Tone</label>
          <div className="flex gap-2">
            {SKIN_TONES.map((tone) => (
              <button
                key={tone.id}
                onClick={() => {
                  setSelectedTone(tone.value);
                  if (currentAvatar) {
                    const url = generateAvatarUrl({
                      gender: selectedGender,
                      bodyType: selectedType === "all" ? (selectedGender === "female" ? "hourglass" : "rectangle") : selectedType,
                      skinTone: tone.value,
                      hairStyle: selectedHairStyle,
                      hairColor: selectedHairColor,
                      seed: `${Date.now()}-${Math.random()}`, // Add a unique seed
                    });
                    onAvatarChange(url);
                  }
                }}
                style={{ backgroundColor: tone.color }}
                className={`w-8 h-8 rounded-full border-2 ${
                  selectedTone === tone.value ? "border-blue-500" : "border-transparent"
                }`}
                title={tone.label}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Hair Style</label>
          <select
            value={selectedHairStyle}
            onChange={(e) => {
              setSelectedHairStyle(e.target.value);
              if (currentAvatar) {
                const url = generateAvatarUrl({
                  gender: selectedGender,
                  bodyType: selectedType === "all" ? (selectedGender === "female" ? "hourglass" : "rectangle") : selectedType,
                  skinTone: selectedTone,
                  hairStyle: e.target.value,
                  hairColor: selectedHairColor,
                  seed: `${Date.now()}-${Math.random()}`, // Add a unique seed
                });
                onAvatarChange(url);
              }
            }}
            className="w-full p-2 border rounded"
          >
            {HAIR_STYLES[selectedGender].map((style) => (
              <option key={style.id} value={style.value}>
                {style.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Hair Color</label>
          <div className="flex gap-2">
            {HAIR_COLORS.map((color) => (
              <button
                key={color.id}
                onClick={() => {
                  setSelectedHairColor(color.value);
                  if (currentAvatar) {
                    const url = generateAvatarUrl({
                      gender: selectedGender,
                      bodyType: selectedType === "all" ? (selectedGender === "female" ? "hourglass" : "rectangle") : selectedType,
                      skinTone: selectedTone,
                      hairStyle: selectedHairStyle,
                      hairColor: color.value,
                      seed: `${Date.now()}-${Math.random()}`, // Add a unique seed
                    });
                    onAvatarChange(url);
                  }
                }}
                style={{ backgroundColor: `#${color.value}` }}
                className={`w-8 h-8 rounded-full border-2 ${
                  selectedHairColor === color.value ? "border-blue-500" : "border-transparent"
                }`}
                title={color.label}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {filteredAvatars.map((avatar) => (
          <button
            key={avatar.id}
            onClick={() => handleAvatarSelect(avatar)}
            className="p-2 border rounded hover:border-blue-500"
          >
            <div className="relative w-full h-32">
              <Image
                src={getAvatarUrl(avatar)}
                alt={avatar.label}
                fill
                className="object-contain"
                sizes="(max-width: 768px) 100vw, 8rem"
                onError={handleImageError}
                unoptimized
                priority
                loading="eager"
              />
            </div>
            <p className="text-sm text-center mt-2">{avatar.label}</p>
          </button>
        ))}
      </div>

      {imageError && (
        <div className="text-red-500 text-center mt-4">
          Failed to load avatar image. Please try again.
        </div>
      )}

      <div className="flex justify-center mt-6">
        <button
          onClick={handleContinue}
          disabled={!currentAvatar}
          className={`px-6 py-2 rounded-lg font-medium ${
            currentAvatar
              ? "bg-blue-500 text-white hover:bg-blue-600"
              : "bg-gray-300 text-gray-500 cursor-not-allowed"
          }`}
        >
          Continue
        </button>
      </div>
    </div>
  );
} 