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
import { ALLOWED_STYLE_TAGS, StyleTag } from '@/lib/constants';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';

interface StyleTagSelectorProps {
  value: StyleTag[];
  onChange: (value: StyleTag[]) => void;
  className?: string;
}

export function StyleTagSelector({
  value,
  onChange,
  className
}: StyleTagSelectorProps) {
  const [open, setOpen] = React.useState(false);

  const handleSelect = (style: StyleTag) => {
    if (value.includes(style)) {
      onChange(value.filter(s => s !== style));
    } else {
      onChange([...value, style]);
    }
  };

  const handleRemove = (style: StyleTag) => {
    onChange(value.filter(s => s !== style));
  };

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex flex-wrap gap-2">
        {value.map((style) => (
          <Badge
            key={style}
            variant="secondary"
            className="flex items-center gap-1 px-3 py-1"
          >
            {style}
            <button
              onClick={() => handleRemove(style)}
              className="ml-1 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              <X className="h-3 w-3" />
              <span className="sr-only">Remove {style}</span>
            </button>
          </Badge>
        ))}
      </div>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between"
          >
            {value.length === 0
              ? "Select style tags..."
              : `${value.length} style tag${value.length === 1 ? "" : "s"} selected`}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-full p-0">
          <Command>
            <CommandInput placeholder="Search style tags..." />
            <CommandEmpty>No style tag found.</CommandEmpty>
            <CommandGroup>
              {ALLOWED_STYLE_TAGS.map((style) => (
                <CommandItem
                  key={style}
                  value={style}
                  onSelect={() => handleSelect(style)}
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4",
                      value.includes(style) ? "opacity-100" : "opacity-0"
                    )}
                  />
                  {style}
                </CommandItem>
              ))}
            </CommandGroup>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
} 