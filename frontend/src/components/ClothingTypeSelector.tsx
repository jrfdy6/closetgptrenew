import React from 'react';
import { Check, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { CLOTHING_TYPES, TYPE_MAPPING, ClothingType } from '@/lib/constants';

interface ClothingTypeSelectorProps {
  value: ClothingType;
  onChange: (value: ClothingType) => void;
  className?: string;
}

// Group types by category for better organization
const TYPE_GROUPS = {
  "Tops": [
    { value: CLOTHING_TYPES.SHIRT, label: "Shirt" },
    { value: CLOTHING_TYPES.SWEATER, label: "Sweater" },
  ],
  "Bottoms": [
    { value: CLOTHING_TYPES.PANTS, label: "Pants" },
    { value: CLOTHING_TYPES.SKIRT, label: "Skirt" },
  ],
  "One-Piece": [
    { value: CLOTHING_TYPES.DRESS, label: "Dress" },
  ],
  "Outerwear": [
    { value: CLOTHING_TYPES.JACKET, label: "Jacket" },
  ],
  "Footwear": [
    { value: CLOTHING_TYPES.SHOES, label: "Shoes" },
  ],
  "Accessories": [
    { value: CLOTHING_TYPES.ACCESSORY, label: "Accessory" },
  ],
  "Other": [
    { value: CLOTHING_TYPES.OTHER, label: "Other" },
  ],
} as const;

export function ClothingTypeSelector({
  value,
  onChange,
  className
}: ClothingTypeSelectorProps) {
  const [open, setOpen] = React.useState(false);

  // Get the display name for the current value
  const currentLabel = Object.values(TYPE_GROUPS)
    .flat()
    .find(item => item.value === value)?.label || "Select type...";

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn("w-full justify-between", className)}
        >
          {currentLabel}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0">
        <Command>
          <CommandInput placeholder="Search clothing type..." />
          <CommandEmpty>No type found.</CommandEmpty>
          {Object.entries(TYPE_GROUPS).map(([group, types]) => (
            <CommandGroup key={group} heading={group}>
              {types.map(({ value: typeValue, label }) => (
                <CommandItem
                  key={typeValue}
                  value={typeValue}
                  onSelect={() => {
                    onChange(typeValue);
                    setOpen(false);
                  }}
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4",
                      value === typeValue ? "opacity-100" : "opacity-0"
                    )}
                  />
                  {label}
                </CommandItem>
              ))}
            </CommandGroup>
          ))}
        </Command>
      </PopoverContent>
    </Popover>
  );
}

// Helper function to get the display name for a type
export function getTypeDisplayName(type: string): string {
  // Find the first key in TYPE_MAPPING that maps to this type
  const displayName = Object.entries(TYPE_MAPPING).find(
    ([_, value]) => value === type
  )?.[0];

  return displayName || type;
}

// Helper function to get all subtypes for a type
export function getSubtypesForType(type: ClothingType): string[] {
  return Object.entries(TYPE_MAPPING)
    .filter(([_, value]) => value === type)
    .map(([key]) => key);
} 