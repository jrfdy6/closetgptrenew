"use client";

import { useState, useRef, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { X, Plus, Check, Edit3 } from "lucide-react";

interface InlineEditableBadgeProps {
  value: string | string[];
  onSave: (newValue: string | string[]) => void;
  type: 'single' | 'multi';
  options?: string[];
  placeholder?: string;
  className?: string;
  variant?: 'default' | 'outline' | 'secondary';
  allowCustom?: boolean;
}

export default function InlineEditableBadge({
  value,
  onSave,
  type,
  options = [],
  placeholder = "Add...",
  className = "",
  variant = "outline",
  allowCustom = true
}: InlineEditableBadgeProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState("");
  const [multiValues, setMultiValues] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isEditing]);

  const handleStartEdit = () => {
    if (type === 'multi') {
      setMultiValues(Array.isArray(value) ? value : []);
    } else {
      setEditValue(typeof value === 'string' ? value : '');
    }
    setIsEditing(true);
  };

  const handleSave = () => {
    if (type === 'multi') {
      onSave(multiValues);
    } else {
      onSave(editValue);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditValue("");
    setMultiValues([]);
  };

  const handleAddMultiValue = (newValue: string) => {
    if (newValue && !multiValues.includes(newValue)) {
      setMultiValues([...multiValues, newValue]);
    }
  };

  const handleRemoveMultiValue = (valueToRemove: string) => {
    setMultiValues(multiValues.filter(v => v !== valueToRemove));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (isEditing) {
    if (type === 'multi') {
      return (
        <div className="space-y-2">
          <div className="flex flex-wrap gap-1">
            {multiValues.map((val, index) => (
              <Badge key={index} variant="default" className="text-xs">
                {val}
                <button
                  onClick={() => handleRemoveMultiValue(val)}
                  className="ml-1 hover:text-red-500"
                >
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            ))}
          </div>
          <div className="flex gap-1">
            {options.length > 0 ? (
              <Select onValueChange={handleAddMultiValue}>
                <SelectTrigger className="h-6 text-xs">
                  <SelectValue placeholder="Add..." />
                </SelectTrigger>
                <SelectContent>
                  {options.filter(opt => !multiValues.includes(opt)).map(option => (
                    <SelectItem key={option} value={option}>
                      {option}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <Input
                ref={inputRef}
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleAddMultiValue(editValue);
                    setEditValue("");
                  }
                }}
                placeholder={placeholder}
                className="h-6 text-xs"
              />
            )}
            <Button size="sm" variant="ghost" onClick={() => handleAddMultiValue(editValue)} className="h-6 w-6 p-0">
              <Plus className="w-3 h-3" />
            </Button>
          </div>
          <div className="flex gap-1">
            <Button size="sm" onClick={handleSave} className="h-6 text-xs">
              <Check className="w-3 h-3" />
            </Button>
            <Button size="sm" variant="outline" onClick={handleCancel} className="h-6 text-xs">
              <X className="w-3 h-3" />
            </Button>
          </div>
        </div>
      );
    } else {
      return (
        <div className="flex gap-1">
          {options.length > 0 ? (
            <Select value={editValue} onValueChange={setEditValue}>
              <SelectTrigger className="h-6 text-xs">
                <SelectValue placeholder="Select..." />
              </SelectTrigger>
              <SelectContent>
                {options.map(option => (
                  <SelectItem key={option} value={option}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <Input
              ref={inputRef}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={placeholder}
              className="h-6 text-xs"
            />
          )}
          <Button size="sm" onClick={handleSave} className="h-6 text-xs">
            <Check className="w-3 h-3" />
          </Button>
          <Button size="sm" variant="outline" onClick={handleCancel} className="h-6 text-xs">
            <X className="w-3 h-3" />
          </Button>
        </div>
      );
    }
  }

  // Display mode
  if (type === 'multi' && Array.isArray(value) && value.length > 0) {
    return (
      <div className="flex flex-wrap gap-1">
        {value.slice(0, 2).map((val, index) => (
          <Badge key={index} variant={variant} className={`text-xs cursor-pointer hover:bg-opacity-80 ${className}`}>
            {val}
          </Badge>
        ))}
        {value.length > 2 && (
          <Badge variant={variant} className={`text-xs ${className}`}>
            +{value.length - 2}
          </Badge>
        )}
        <button
          onClick={handleStartEdit}
          className="opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <Edit3 className="w-3 h-3 text-gray-400 hover:text-gray-600" />
        </button>
      </div>
    );
  } else if (type === 'single' && value) {
    return (
      <div className="flex items-center gap-1">
        <Badge variant={variant} className={`text-xs cursor-pointer hover:bg-opacity-80 ${className}`}>
          {value}
        </Badge>
        <button
          onClick={handleStartEdit}
          className="opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <Edit3 className="w-3 h-3 text-gray-400 hover:text-gray-600" />
        </button>
      </div>
    );
  } else {
    return (
      <button
        onClick={handleStartEdit}
        className="text-xs text-gray-400 hover:text-gray-600 border border-dashed border-gray-300 rounded px-2 py-1 hover:border-gray-400"
      >
        <Plus className="w-3 h-3 inline mr-1" />
        {placeholder}
      </button>
    );
  }
}
