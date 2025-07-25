'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface ValidationRules {
  material_climate_rules: Record<string, { max_temp_f: number; min_temp_f: number }>;
  seasonal_rules: Record<string, { months: number[]; min_temp_f: number }>;
  occasion_rules: Record<string, { min_items: number; requires_jacket: boolean }>;
  layering_rules: { max_layers: number; min_layers_cold: number; max_layers_hot: number };
  color_rules: { max_colors: number; require_neutral_base: boolean; allow_patterns: boolean };
  metadata: { version: string; last_updated: number; created_at: number };
}

interface RuleHistory {
  timestamp: number;
  timestamp_readable: string;
  user_id: string;
  rule_path: string;
  old_value: any;
  new_value: any;
}

export default function ValidationRulesPage() {
  const [rules, setRules] = useState<ValidationRules | null>(null);
  const [history, setHistory] = useState<RuleHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form states
  const [newMaterial, setNewMaterial] = useState('');
  const [newMaxTemp, setNewMaxTemp] = useState('');
  const [newMinTemp, setNewMinTemp] = useState('');
  const [updateRulePath, setUpdateRulePath] = useState('');
  const [updateRuleValue, setUpdateRuleValue] = useState('');

  const fetchRules = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/validation-rules');
      if (!response.ok) {
        throw new Error(`Failed to fetch rules: ${response.status}`);
      }
      const data = await response.json();
      setRules(data.rules);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await fetch('/api/validation-rules/history');
      if (!response.ok) {
        throw new Error(`Failed to fetch history: ${response.status}`);
      }
      const data = await response.json();
      setHistory(data.history || []);
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  const addMaterialRule = async () => {
    if (!newMaterial || !newMaxTemp || !newMinTemp) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/validation-rules/material', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          material: newMaterial.toLowerCase(),
          max_temp_f: parseInt(newMaxTemp),
          min_temp_f: parseInt(newMinTemp)
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to add material rule: ${response.status}`);
      }

      const data = await response.json();
      if (data.success) {
        setNewMaterial('');
        setNewMaxTemp('');
        setNewMinTemp('');
        await fetchRules();
        await fetchHistory();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const updateRule = async () => {
    if (!updateRulePath || !updateRuleValue) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/validation-rules/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rule_path: updateRulePath,
          new_value: isNaN(Number(updateRuleValue)) ? updateRuleValue : Number(updateRuleValue)
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to update rule: ${response.status}`);
      }

      const data = await response.json();
      if (data.success) {
        setUpdateRulePath('');
        setUpdateRuleValue('');
        await fetchRules();
        await fetchHistory();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
    fetchHistory();
  }, []);

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  if (loading && !rules) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center">Loading validation rules...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Validation Rules Management</h1>
        <Button onClick={fetchRules} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh Rules'}
        </Button>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-700 font-medium">Error: {error}</p>
          </CardContent>
        </Card>
      )}

      {rules && (
        <Tabs defaultValue="rules" className="space-y-4">
          <TabsList>
            <TabsTrigger value="rules">Current Rules</TabsTrigger>
            <TabsTrigger value="add">Add Material Rule</TabsTrigger>
            <TabsTrigger value="update">Update Rule</TabsTrigger>
            <TabsTrigger value="history">Change History</TabsTrigger>
          </TabsList>

          <TabsContent value="rules" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Material Climate Rules */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    Material Climate Rules
                    <Badge variant="secondary">{Object.keys(rules.material_climate_rules).length} materials</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(rules.material_climate_rules).map(([material, temps]) => (
                      <div key={material} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="font-medium capitalize">{material}</span>
                        <span className="text-sm text-gray-600">
                          {temps.min_temp_f}°F - {temps.max_temp_f}°F
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Other Rules */}
              <Card>
                <CardHeader>
                  <CardTitle>Other Rules</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium">Layering Rules</h4>
                      <p className="text-sm text-gray-600">
                        Max: {rules.layering_rules.max_layers}, 
                        Cold: {rules.layering_rules.min_layers_cold}, 
                        Hot: {rules.layering_rules.max_layers_hot}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium">Color Rules</h4>
                      <p className="text-sm text-gray-600">
                        Max colors: {rules.color_rules.max_colors}, 
                        Neutral base: {rules.color_rules.require_neutral_base ? 'Yes' : 'No'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Metadata</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Version:</span> {rules.metadata.version}
                  </div>
                  <div>
                    <span className="font-medium">Last Updated:</span> {formatTimestamp(rules.metadata.last_updated)}
                  </div>
                  <div>
                    <span className="font-medium">Created:</span> {formatTimestamp(rules.metadata.created_at)}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="add" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Add New Material Rule</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="material">Material</Label>
                    <Input
                      id="material"
                      value={newMaterial}
                      onChange={(e) => setNewMaterial(e.target.value)}
                      placeholder="e.g., polyester"
                    />
                  </div>
                  <div>
                    <Label htmlFor="maxTemp">Max Temperature (°F)</Label>
                    <Input
                      id="maxTemp"
                      type="number"
                      value={newMaxTemp}
                      onChange={(e) => setNewMaxTemp(e.target.value)}
                      placeholder="e.g., 85"
                    />
                  </div>
                  <div>
                    <Label htmlFor="minTemp">Min Temperature (°F)</Label>
                    <Input
                      id="minTemp"
                      type="number"
                      value={newMinTemp}
                      onChange={(e) => setNewMinTemp(e.target.value)}
                      placeholder="e.g., 55"
                    />
                  </div>
                </div>
                <Button onClick={addMaterialRule} disabled={loading} className="mt-4">
                  {loading ? 'Adding...' : 'Add Material Rule'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="update" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Update Rule</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="rulePath">Rule Path</Label>
                    <Input
                      id="rulePath"
                      value={updateRulePath}
                      onChange={(e) => setUpdateRulePath(e.target.value)}
                      placeholder="e.g., material_climate_rules.wool.max_temp_f"
                    />
                  </div>
                  <div>
                    <Label htmlFor="ruleValue">New Value</Label>
                    <Input
                      id="ruleValue"
                      value={updateRuleValue}
                      onChange={(e) => setUpdateRuleValue(e.target.value)}
                      placeholder="e.g., 80"
                    />
                  </div>
                </div>
                <Button onClick={updateRule} disabled={loading} className="mt-4">
                  {loading ? 'Updating...' : 'Update Rule'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Rule Change History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {history.map((change, index) => (
                    <div key={index} className="p-3 bg-gray-50 rounded">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">{change.rule_path}</p>
                          <p className="text-sm text-gray-600">
                            {change.old_value ? `Old: ${JSON.stringify(change.old_value)}` : 'Added'} → 
                            {change.new_value ? ` New: ${JSON.stringify(change.new_value)}` : ' Removed'}
                          </p>
                        </div>
                        <div className="text-right text-sm text-gray-500">
                          <p>{change.timestamp_readable}</p>
                          <p>User: {change.user_id}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                  {history.length === 0 && (
                    <p className="text-gray-500 text-center py-4">No changes recorded yet.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
