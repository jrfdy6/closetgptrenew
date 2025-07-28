"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getWeatherIcon } from "@/lib/weather";
import { useWeather } from "@/hooks/useWeather";
import type { WeatherData } from "@/types/weather";

export function WeatherDisplay() {
  const { weather, loading, error } = useWeather();

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Current Weather</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Loading weather data...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Current Weather</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-500">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!weather) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Current Weather</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p className="text-2xl font-bold">{weather.temperature}°F</p>
          <p className="text-lg">{getWeatherIcon(weather.condition)} {weather.condition}</p>
          <p className="text-sm text-muted-foreground">{weather.location}</p>
          <div className="text-sm text-muted-foreground">
            <p>Humidity: {weather.humidity}%</p>
            <p>Wind: {weather.wind_speed} mph</p>
            {weather.precipitation > 0 && (
              <p>Precipitation: {weather.precipitation} mm</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}