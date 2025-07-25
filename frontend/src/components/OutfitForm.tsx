'use client';

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Save, Trash } from "lucide-react";
import Image from "next/image";
import { ClothingItem, Outfit } from "../shared/types/index";

interface OutfitFormProps {
  outfitId: string;
}

const OCCASIONS = [
  "Work",
  "Casual",
  "Party",
  "Date Night",
  "Formal",
  "Sport",
  "Travel",
];

const WEATHER_TYPES = [
  { value: "sunny", label: "Sunny" },
  { value: "cloudy", label: "Cloudy" },
  { value: "rainy", label: "Rainy" },
  { value: "snowy", label: "Snowy" },
];

export default function OutfitForm({ outfitId }: OutfitFormProps) {
  const router = useRouter();
  const [outfit, setOutfit] = useState<Outfit>({
    id: "",
    name: "",
    description: "",
    items: [
      {
        id: "1",
        name: "Blue T-Shirt",
        type: "shirt",
        color: "blue",
        season: ["spring", "summer"],
        imageUrl: "/placeholder.jpg",
        tags: ["casual"],
        style: ["casual"],
        userId: "user1",
        dominantColors: [],
        matchingColors: [],
        occasion: ["casual"],
        createdAt: Date.now(),
        updatedAt: Date.now()
      },
      {
        id: "2",
        name: "Black Jeans",
        type: "pants",
        color: "black",
        season: ["spring", "summer", "fall"],
        imageUrl: "/placeholder.jpg",
        tags: ["casual"],
        style: ["casual"],
        userId: "user1",
        dominantColors: [],
        matchingColors: [],
        occasion: ["casual"],
        createdAt: Date.now(),
        updatedAt: Date.now()
      }
    ],
    occasion: "casual",
    season: "spring",
    style: "casual",
    styleTags: ["casual"],
    createdAt: Date.now(),
    updatedAt: Date.now()
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchOutfit = async () => {
      try {
        // Simulate API call
        const data: Outfit = {
          id: outfitId,
          name: "Casual Summer Day",
          description: "A classic casual combination perfect for a sunny day. The white t-shirt keeps you cool while the blue jeans provide a timeless look.",
          items: [
            {
              id: "1",
              name: "White T-Shirt",
              type: "shirt",
              color: "white",
              season: ["spring", "summer"],
              imageUrl: "/placeholder.jpg",
              tags: ["casual"],
              style: ["casual"],
              userId: "user1",
              dominantColors: [],
              matchingColors: [],
              occasion: ["casual"],
              createdAt: Date.now(),
              updatedAt: Date.now()
            },
            {
              id: "2",
              name: "Blue Jeans",
              type: "pants",
              color: "blue",
              season: ["spring", "summer", "fall"],
              imageUrl: "/placeholder.jpg",
              tags: ["casual"],
              style: ["casual"],
              userId: "user1",
              dominantColors: [],
              matchingColors: [],
              occasion: ["casual"],
              createdAt: Date.now(),
              updatedAt: Date.now()
            }
          ],
          occasion: "casual",
          season: "spring",
          style: "casual",
          styleTags: ["casual"],
          createdAt: Date.now(),
          updatedAt: Date.now()
        };

        setOutfit(data);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching outfit:", err);
        setLoading(false);
      }
    };

    fetchOutfit();
  }, [outfitId]);

  const handleSave = async () => {
    if (!outfit) return;

    setSaving(true);
    try {
      // Here you would typically save the outfit to your database
      await new Promise((resolve) => setTimeout(resolve, 1000));
      router.push("/outfits");
    } catch (err) {
      console.error("Error saving outfit:", err);
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!outfit) return;

    try {
      // Here you would typically delete the outfit from your database
      await new Promise((resolve) => setTimeout(resolve, 1000));
      router.push("/outfits");
    } catch (err) {
      console.error("Error deleting outfit:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!outfit) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <h2 className="mb-4 text-2xl font-bold">Outfit not found</h2>
        <p className="mb-4 text-gray-600">
          The outfit you&apos;re looking for doesn&apos;t exist or has been deleted.
        </p>
        <button
          onClick={() => router.push("/outfits")}
          className="flex items-center text-blue-600 hover:text-blue-800"
        >
          Back to Outfits
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Outfit Details */}
      <div className="space-y-6">
        <div>
          <label htmlFor="name" className="mb-2 block text-sm font-medium">
            Outfit Name
          </label>
          <input
            id="name"
            value={outfit.name}
            onChange={(e) => setOutfit({ ...outfit, name: e.target.value })}
            placeholder="Enter outfit name"
            className="w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <label htmlFor="occasion" className="mb-2 block text-sm font-medium">
              Occasion
            </label>
            <select
              id="occasion"
              value={outfit.occasion}
              onChange={(e) => setOutfit({ ...outfit, occasion: e.target.value })}
              className="w-full rounded-md border border-gray-300 p-2"
            >
              {OCCASIONS.map((occasion) => (
                <option key={occasion} value={occasion}>
                  {occasion}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="weather" className="mb-2 block text-sm font-medium">
              Weather
            </label>
            <select
              id="weather"
              value={outfit.weather}
              onChange={(e) => setOutfit({ ...outfit, weather: e.target.value })}
              className="w-full rounded-md border border-gray-300 p-2"
            >
              {WEATHER_TYPES.map(({ value, label }) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="explanation" className="mb-2 block text-sm font-medium">
            Explanation
          </label>
          <textarea
            id="explanation"
            value={outfit.explanation}
            onChange={(e) => setOutfit({ ...outfit, explanation: e.target.value })}
            placeholder="Explain why this outfit works..."
            className="w-full rounded-md border border-gray-300 p-2"
            rows={4}
          />
        </div>
      </div>

      {/* Items Grid */}
      <div>
        <h3 className="mb-4 text-xl font-semibold">Items</h3>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {outfit.items.map((item) => (
            <div key={item.id} className="rounded-lg border border-gray-200 p-4">
              <div className="mb-4 aspect-square overflow-hidden rounded-md relative">
                <Image
                  src={item.imageUrl}
                  alt={item.name}
                  fill
                  className="object-cover"
                />
              </div>
              <div>
                <h4 className="mb-1 font-medium">{item.name}</h4>
                <div className="text-sm text-gray-600">
                  {item.type} • {item.color}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end space-x-4">
        <button
          onClick={handleDelete}
          className="flex items-center rounded-md bg-red-600 px-4 py-2 text-white hover:bg-red-700"
        >
          <Trash className="mr-2 h-4 w-4" />
          Delete Outfit
        </button>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          <Save className="mr-2 h-4 w-4" />
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </div>
    </div>
  );
} 