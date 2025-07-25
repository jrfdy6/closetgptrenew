"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { StyleTagSelector } from '@/components/StyleTagSelector';
import { ALLOWED_STYLE_TYPES, StyleType } from '@/lib/constants';
import { Plus, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

interface StyleRule {
  id: string;
  name: string;
  description: string;
  styles: StyleType[];
  conditions: {
    weather?: {
      minTemp?: number;
      maxTemp?: number;
      conditions?: string[];
    };
    occasion?: string[];
    season?: string[];
  };
}

export default function StyleRules() {
  const [rules, setRules] = useState<StyleRule[]>([]);
  const [newRule, setNewRule] = useState<Partial<StyleRule>>({
    name: '',
    description: '',
    styles: [],
    conditions: {}
  });

  const handleAddRule = () => {
    if (!newRule.name || !newRule.description || !newRule.styles?.length) {
      toast.error('Please fill in all required fields');
      return;
    }

    const rule: StyleRule = {
      id: Date.now().toString(),
      name: newRule.name,
      description: newRule.description,
      styles: newRule.styles as StyleType[],
      conditions: newRule.conditions || {}
    };

    setRules([...rules, rule]);
    setNewRule({
      name: '',
      description: '',
      styles: [],
      conditions: {}
    });
    toast.success('Style rule added successfully');
  };

  const handleDeleteRule = (id: string) => {
    setRules(rules.filter(rule => rule.id !== id));
    toast.success('Style rule removed');
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-6">Style Rules</h2>
        
        {/* Add New Rule Form */}
        <div className="space-y-4 mb-8">
          <div>
            <Label htmlFor="ruleName">Rule Name</Label>
            <Input
              id="ruleName"
              value={newRule.name}
              onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
              placeholder="e.g., Summer Business Casual"
            />
          </div>

          <div>
            <Label htmlFor="ruleDescription">Description</Label>
            <Textarea
              id="ruleDescription"
              value={newRule.description}
              onChange={(e) => setNewRule({ ...newRule, description: e.target.value })}
              placeholder="Describe when and how this rule should be applied"
            />
          </div>

          <div>
            <Label>Style Tags</Label>
            <StyleTagSelector
              value={newRule.styles || []}
              onChange={(styles) => setNewRule({ ...newRule, styles })}
            />
          </div>

          <Button
            onClick={handleAddRule}
            className="w-full"
            disabled={!newRule.name || !newRule.description || !newRule.styles?.length}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Rule
          </Button>
        </div>

        {/* Existing Rules List */}
        <div className="space-y-4">
          {rules.map((rule) => (
            <Card key={rule.id} className="p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{rule.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{rule.description}</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {rule.styles.map((style) => (
                      <span
                        key={style}
                        className="px-2 py-1 bg-gray-100 rounded-full text-sm"
                      >
                        {style}
                      </span>
                    ))}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDeleteRule(rule.id)}
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </Card>
    </div>
  );
} 