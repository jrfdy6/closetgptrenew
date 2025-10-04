/**
 * Enterprise-grade data validation and sanitization
 * Ensures data integrity and security across the application
 */

export interface ValidationRule {
  required?: boolean;
  type?: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'email' | 'url';
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  pattern?: RegExp;
  enum?: any[];
  custom?: (value: any) => boolean | string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  sanitizedValue?: any;
}

export class DataValidator {
  private static instance: DataValidator;
  
  public static getInstance(): DataValidator {
    if (!DataValidator.instance) {
      DataValidator.instance = new DataValidator();
    }
    return DataValidator.instance;
  }

  /**
   * Validate and sanitize outfit generation request
   */
  public validateOutfitRequest(data: any): ValidationResult {
    const errors: string[] = [];
    const sanitized: any = {};

    // Validate occasion
    const occasionResult = this.validateField(data.occasion, {
      required: true,
      type: 'string',
      enum: ['Casual', 'Business', 'Formal', 'Athletic', 'Party', 'Date', 'Interview', 'Weekend', 'Loungewear']
    });
    if (!occasionResult.isValid) errors.push(...occasionResult.errors);
    else sanitized.occasion = occasionResult.sanitizedValue;

    // Validate style
    const styleResult = this.validateField(data.style, {
      required: true,
      type: 'string',
      enum: ['Classic', 'Modern', 'Vintage', 'Bohemian', 'Minimalist', 'Grunge', 'Preppy', 'Streetwear', 'Dark Academia', 'Light Academia', 'Old Money', 'Y2K', 'Avant-Garde', 'Artsy', 'Maximalist', 'Colorblock', 'Business Casual', 'Urban Professional', 'Techwear', 'Hipster', 'Scandinavian', 'Gothic', 'Punk', 'Cyberpunk', 'Edgy', 'Coastal Chic', 'Athleisure', 'Casual Cool']
    });
    if (!styleResult.isValid) errors.push(...styleResult.errors);
    else sanitized.style = styleResult.sanitizedValue;

    // Validate mood
    const moodResult = this.validateField(data.mood, {
      required: true,
      type: 'string',
      enum: ['Confident', 'Relaxed', 'Energetic', 'Professional', 'Romantic', 'Playful', 'Serene', 'Dynamic', 'Bold', 'Subtle']
    });
    if (!moodResult.isValid) errors.push(...moodResult.errors);
    else sanitized.mood = moodResult.sanitizedValue;

    // Validate weather
    const weatherResult = this.validateWeatherData(data.weather);
    if (!weatherResult.isValid) errors.push(...weatherResult.errors);
    else sanitized.weather = weatherResult.sanitizedValue;

    // Validate wardrobe
    const wardrobeResult = this.validateWardrobe(data.wardrobe);
    if (!wardrobeResult.isValid) errors.push(...wardrobeResult.errors);
    else sanitized.wardrobe = wardrobeResult.sanitizedValue;

    // Validate user profile
    const profileResult = this.validateUserProfile(data.user_profile);
    if (!profileResult.isValid) errors.push(...profileResult.errors);
    else sanitized.user_profile = profileResult.sanitizedValue;

    return {
      isValid: errors.length === 0,
      errors,
      sanitizedValue: errors.length === 0 ? sanitized : undefined
    };
  }

  /**
   * Validate weather data
   */
  private validateWeatherData(weather: any): ValidationResult {
    const errors: string[] = [];
    const sanitized: any = {};

    if (!weather || typeof weather !== 'object') {
      return { isValid: false, errors: ['Weather data is required and must be an object'] };
    }

    // Temperature
    const tempResult = this.validateField(weather.temperature, {
      required: true,
      type: 'number',
      min: -50,
      max: 150
    });
    if (!tempResult.isValid) errors.push(...tempResult.errors);
    else sanitized.temperature = Math.round(tempResult.sanitizedValue * 10) / 10; // Round to 1 decimal

    // Condition
    const conditionResult = this.validateField(weather.condition, {
      required: true,
      type: 'string',
      enum: ['Clear', 'Cloudy', 'Rainy', 'Snowy', 'Foggy', 'Windy', 'Stormy', 'Overcast']
    });
    if (!conditionResult.isValid) errors.push(...conditionResult.errors);
    else sanitized.condition = conditionResult.sanitizedValue;

    // Optional fields
    sanitized.humidity = Math.max(0, Math.min(100, weather.humidity || 0));
    sanitized.wind_speed = Math.max(0, weather.wind_speed || 0);
    sanitized.location = this.sanitizeString(weather.location || 'Unknown');
    sanitized.precipitation = Math.max(0, weather.precipitation || 0);

    return {
      isValid: errors.length === 0,
      errors,
      sanitizedValue: errors.length === 0 ? sanitized : undefined
    };
  }

  /**
   * Validate wardrobe items
   */
  private validateWardrobe(wardrobe: any): ValidationResult {
    const errors: string[] = [];

    if (!Array.isArray(wardrobe)) {
      return { isValid: false, errors: ['Wardrobe must be an array'] };
    }

    if (wardrobe.length === 0) {
      console.warn('⚠️ Wardrobe is empty - outfit generation may use fallback items');
      // Allow empty wardrobe - let backend handle gracefully
      return { isValid: true, errors: [], sanitizedValue: [] };
    }

    if (wardrobe.length > 500) {
      return { isValid: false, errors: ['Wardrobe too large (max 500 items)'] };
    }

    const sanitized = wardrobe.map((item: any, index: number) => {
      const itemResult = this.validateWardrobeItem(item);
      if (!itemResult.isValid) {
        errors.push(`Item ${index + 1}: ${itemResult.errors.join(', ')}`);
        return null;
      }
      return itemResult.sanitizedValue;
    }).filter(Boolean);

    // Check for duplicate IDs
    const ids = sanitized.map((item: any) => item.id);
    const duplicateIds = ids.filter((id: string, index: number) => ids.indexOf(id) !== index);
    if (duplicateIds.length > 0) {
      errors.push(`Duplicate item IDs found: ${duplicateIds.join(', ')}`);
    }

    return {
      isValid: errors.length === 0,
      errors,
      sanitizedValue: errors.length === 0 ? sanitized : undefined
    };
  }

  /**
   * Validate individual wardrobe item
   */
  private validateWardrobeItem(item: any): ValidationResult {
    const errors: string[] = [];
    const sanitized: any = {};

    if (!item || typeof item !== 'object') {
      return { isValid: false, errors: ['Item must be an object'] };
    }

    // ID
    const idResult = this.validateField(item.id, {
      required: true,
      type: 'string',
      minLength: 1,
      maxLength: 100,
      pattern: /^[a-zA-Z0-9_-]+$/
    });
    if (!idResult.isValid) errors.push(...idResult.errors);
    else sanitized.id = idResult.sanitizedValue;

    // Name
    const nameResult = this.validateField(item.name, {
      required: true,
      type: 'string',
      minLength: 1,
      maxLength: 200
    });
    if (!nameResult.isValid) errors.push(...nameResult.errors);
    else sanitized.name = this.sanitizeString(nameResult.sanitizedValue);

    // Type
    const typeResult = this.validateField(item.type, {
      required: true,
      type: 'string',
      enum: ['T_SHIRT', 'SHIRT', 'BLOUSE', 'SWEATER', 'JACKET', 'BLAZER', 'PANTS', 'JEANS', 'SHORTS', 'SKIRT', 'DRESS', 'SHOES', 'SNEAKERS', 'BOOTS', 'SANDALS', 'HEELS', 'ACCESSORY', 'BELT', 'HAT', 'SCARF', 'OTHER']
    });
    if (!typeResult.isValid) errors.push(...typeResult.errors);
    else sanitized.type = typeResult.sanitizedValue;

    // Color
    const colorResult = this.validateField(item.color, {
      required: true,
      type: 'string',
      minLength: 1,
      maxLength: 50
    });
    if (!colorResult.isValid) errors.push(...colorResult.errors);
    else sanitized.color = this.sanitizeString(colorResult.sanitizedValue);

    // Optional fields with defaults
    sanitized.season = this.validateStringArray(item.season) || ['all'];
    sanitized.tags = this.validateStringArray(item.tags) || [];
    sanitized.style = this.validateStringArray(item.style) || [];
    sanitized.occasion = this.validateStringArray(item.occasion) || ['casual'];
    sanitized.dominantColors = this.validateStringArray(item.dominantColors) || [];
    sanitized.matchingColors = this.validateStringArray(item.matchingColors) || [];
    sanitized.imageUrl = this.sanitizeUrl(item.imageUrl) || '';
    sanitized.brand = this.sanitizeString(item.brand) || null;
    sanitized.wearCount = Math.max(0, Math.floor(item.wearCount || 0));
    sanitized.favorite_score = Math.max(0, Math.min(10, item.favorite_score || 0));

    return {
      isValid: errors.length === 0,
      errors,
      sanitizedValue: errors.length === 0 ? sanitized : undefined
    };
  }

  /**
   * Validate user profile
   */
  private validateUserProfile(profile: any): ValidationResult {
    const errors: string[] = [];
    const sanitized: any = {};

    if (!profile || typeof profile !== 'object') {
      return { isValid: false, errors: ['User profile is required and must be an object'] };
    }

    // ID
    const idResult = this.validateField(profile.id, {
      required: true,
      type: 'string',
      minLength: 1,
      maxLength: 100
    });
    if (!idResult.isValid) errors.push(...idResult.errors);
    else sanitized.id = idResult.sanitizedValue;

    // Name
    sanitized.name = this.sanitizeString(profile.name) || 'User';
    
    // Email
    if (profile.email) {
      const emailResult = this.validateField(profile.email, {
        type: 'email'
      });
      if (!emailResult.isValid) errors.push(...emailResult.errors);
      else sanitized.email = emailResult.sanitizedValue;
    } else {
      sanitized.email = '';
    }

    // Gender
    sanitized.gender = ['male', 'female', 'non-binary', 'other'].includes(profile.gender) 
      ? profile.gender 
      : 'male';

    // Age
    sanitized.age = Math.max(13, Math.min(120, Math.floor(profile.age || 25)));

    // Height
    sanitized.height = this.sanitizeString(profile.height) || '';

    // Weight
    sanitized.weight = this.sanitizeString(profile.weight) || '';

    // Body type
    sanitized.bodyType = this.sanitizeString(profile.bodyType) || 'average';

    // Style preferences
    sanitized.style_preferences = this.validateStringArray(profile.style_preferences) || [];
    sanitized.color_preferences = this.validateStringArray(profile.color_preferences) || [];
    sanitized.size_preferences = this.validateStringArray(profile.size_preferences) || [];

    return {
      isValid: errors.length === 0,
      errors,
      sanitizedValue: errors.length === 0 ? sanitized : undefined
    };
  }

  /**
   * Generic field validation
   */
  private validateField(value: any, rules: ValidationRule): ValidationResult {
    const errors: string[] = [];

    // Required check
    if (rules.required && (value === undefined || value === null || value === '')) {
      errors.push('Field is required');
      return { isValid: false, errors };
    }

    if (value === undefined || value === null || value === '') {
      return { isValid: true, errors: [], sanitizedValue: value };
    }

    // Type check
    if (rules.type) {
      const typeValid = this.checkType(value, rules.type);
      if (!typeValid) {
        errors.push(`Expected ${rules.type}, got ${typeof value}`);
        return { isValid: false, errors };
      }
    }

    // String validations
    if (typeof value === 'string') {
      if (rules.minLength !== undefined && value.length < rules.minLength) {
        errors.push(`Minimum length is ${rules.minLength}`);
      }
      if (rules.maxLength !== undefined && value.length > rules.maxLength) {
        errors.push(`Maximum length is ${rules.maxLength}`);
      }
      if (rules.pattern && !rules.pattern.test(value)) {
        errors.push('Invalid format');
      }
    }

    // Number validations
    if (typeof value === 'number') {
      if (rules.min !== undefined && value < rules.min) {
        errors.push(`Minimum value is ${rules.min}`);
      }
      if (rules.max !== undefined && value > rules.max) {
        errors.push(`Maximum value is ${rules.max}`);
      }
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push(`Must be one of: ${rules.enum.join(', ')}`);
    }

    // Custom validation
    if (rules.custom) {
      const customResult = rules.custom(value);
      if (customResult !== true) {
        errors.push(typeof customResult === 'string' ? customResult : 'Custom validation failed');
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      sanitizedValue: this.sanitizeValue(value, rules.type)
    };
  }

  /**
   * Check value type
   */
  private checkType(value: any, expectedType: string): boolean {
    switch (expectedType) {
      case 'string':
        return typeof value === 'string';
      case 'number':
        return typeof value === 'number' && !isNaN(value);
      case 'boolean':
        return typeof value === 'boolean';
      case 'array':
        return Array.isArray(value);
      case 'object':
        return typeof value === 'object' && value !== null && !Array.isArray(value);
      case 'email':
        return typeof value === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
      case 'url':
        return typeof value === 'string' && /^https?:\/\/.+/.test(value);
      default:
        return true;
    }
  }

  /**
   * Sanitize value based on type
   */
  private sanitizeValue(value: any, type?: string): any {
    switch (type) {
      case 'string':
        return this.sanitizeString(value);
      case 'number':
        return Number(value);
      case 'boolean':
        return Boolean(value);
      case 'email':
        return this.sanitizeString(value).toLowerCase();
      case 'url':
        return this.sanitizeUrl(value);
      default:
        return value;
    }
  }

  /**
   * Sanitize string (remove dangerous characters)
   */
  private sanitizeString(value: any): string {
    if (typeof value !== 'string') return String(value);
    return value
      .replace(/[<>]/g, '') // Remove potential HTML
      .replace(/[&"']/g, '') // Remove potential script injection
      .trim();
  }

  /**
   * Sanitize URL
   */
  private sanitizeUrl(value: any): string {
    if (typeof value !== 'string') return '';
    try {
      const url = new URL(value);
      return ['http:', 'https:'].includes(url.protocol) ? url.toString() : '';
    } catch {
      return '';
    }
  }

  /**
   * Validate string array
   */
  private validateStringArray(value: any): string[] {
    if (!Array.isArray(value)) return [];
    return value
      .filter(item => typeof item === 'string')
      .map(item => this.sanitizeString(item))
      .filter(item => item.length > 0);
  }
}
