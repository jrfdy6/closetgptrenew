# Firestore Indexes Guide

This guide provides the exact steps to create the required Firestore indexes to resolve the index errors in the outfit generation system.

## Required Indexes

### 1. Wardrobe Collection Indexes

#### Index 1: User + Category + Seasonality
- **Collection**: `wardrobe`
- **Fields**:
  - `userId` (Ascending)
  - `category` (Ascending)
  - `seasonality` (Array contains)
- **Query Type**: Composite
- **Purpose**: Filter items by user, category, and season

#### Index 2: User + Category + Formality
- **Collection**: `wardrobe`
- **Fields**:
  - `userId` (Ascending)
  - `category` (Ascending)
  - `formality` (Ascending)
- **Query Type**: Composite
- **Purpose**: Filter items by user, category, and formality level

#### Index 3: User + Category + Quality Score
- **Collection**: `wardrobe`
- **Fields**:
  - `userId` (Ascending)
  - `category` (Ascending)
  - `quality_score` (Descending)
- **Query Type**: Composite
- **Purpose**: Get high-quality items by category

#### Index 4: User + Category + Pairability Score
- **Collection**: `wardrobe`
- **Fields**:
  - `userId` (Ascending)
  - `category` (Ascending)
  - `pairability_score` (Descending)
- **Query Type**: Composite
- **Purpose**: Get highly pairable items by category

#### Index 5: User + Favorite Items
- **Collection**: `wardrobe`
- **Fields**:
  - `userId` (Ascending)
  - `favorite` (Ascending)
- **Query Type**: Composite
- **Purpose**: Get user's favorite items

#### Index 6: User + Category + Wear Count
- **Collection**: `wardrobe`
- **Fields**:
  - `userId` (Ascending)
  - `category` (Ascending)
  - `wear_count` (Ascending)
- **Query Type**: Composite
- **Purpose**: Get underutilized items

#### Index 7: User + Style Tags
- **Collection**: `wardrobe`
- **Fields**:
  - `userId` (Ascending)
  - `style_tags` (Array contains any)
- **Query Type**: Composite
- **Purpose**: Filter items by style compatibility

#### Index 8: User + Material + Seasonality
- **Collection**: `wardrobe`
- **Fields**:
  - `userId` (Ascending)
  - `material` (Ascending)
  - `seasonality` (Array contains)
- **Query Type**: Composite
- **Purpose**: Weather-appropriate material filtering

### 2. Outfits Collection Indexes

#### Index 9: User + Creation Date Range
- **Collection**: `outfits`
- **Fields**:
  - `user_id` (Ascending)
  - `createdAt` (Ascending)
- **Query Type**: Composite
- **Purpose**: Get outfits within date range

#### Index 10: User + Success Status
- **Collection**: `outfits`
- **Fields**:
  - `user_id` (Ascending)
  - `wasSuccessful` (Ascending)
- **Query Type**: Composite
- **Purpose**: Filter successful vs failed outfits

## How to Create Indexes

### Method 1: Firebase Console (Recommended)

1. **Open Firebase Console**
   - Go to [https://console.firebase.google.com](https://console.firebase.google.com)
   - Select your project

2. **Navigate to Firestore**
   - Click on "Firestore Database" in the left sidebar
   - Click on the "Indexes" tab

3. **Create Composite Index**
   - Click "Create Index"
   - Select the collection (e.g., `wardrobe`)
   - Add the required fields in the correct order
   - Set the query scope to "Collection"
   - Click "Create"

### Method 2: Firebase CLI

1. **Install Firebase CLI** (if not already installed):
   ```bash
   npm install -g firebase-tools
   ```

2. **Login to Firebase**:
   ```bash
   firebase login
   ```

3. **Initialize Firebase** (if not already done):
   ```bash
   firebase init firestore
   ```

4. **Create firestore.indexes.json**:
   ```json
   {
     "indexes": [
       {
         "collectionGroup": "wardrobe",
         "queryScope": "COLLECTION",
         "fields": [
           { "fieldPath": "userId", "order": "ASCENDING" },
           { "fieldPath": "category", "order": "ASCENDING" },
           { "fieldPath": "seasonality", "arrayConfig": "CONTAINS" }
         ]
       },
       {
         "collectionGroup": "wardrobe",
         "queryScope": "COLLECTION",
         "fields": [
           { "fieldPath": "userId", "order": "ASCENDING" },
           { "fieldPath": "category", "order": "ASCENDING" },
           { "fieldPath": "formality", "order": "ASCENDING" }
         ]
       },
       {
         "collectionGroup": "wardrobe",
         "queryScope": "COLLECTION",
         "fields": [
           { "fieldPath": "userId", "order": "ASCENDING" },
           { "fieldPath": "category", "order": "ASCENDING" },
           { "fieldPath": "quality_score", "order": "DESCENDING" }
         ]
       },
       {
         "collectionGroup": "wardrobe",
         "queryScope": "COLLECTION",
         "fields": [
           { "fieldPath": "userId", "order": "ASCENDING" },
           { "fieldPath": "category", "order": "ASCENDING" },
           { "fieldPath": "pairability_score", "order": "DESCENDING" }
         ]
       },
       {
         "collectionGroup": "wardrobe",
         "queryScope": "COLLECTION",
         "fields": [
           { "fieldPath": "userId", "order": "ASCENDING" },
           { "fieldPath": "favorite", "order": "ASCENDING" }
         ]
       },
       {
         "collectionGroup": "wardrobe",
         "queryScope": "COLLECTION",
         "fields": [
           { "fieldPath": "userId", "order": "ASCENDING" },
           { "fieldPath": "category", "order": "ASCENDING" },
           { "fieldPath": "wear_count", "order": "ASCENDING" }
         ]
       },
       {
         "collectionGroup": "wardrobe",
         "queryScope": "COLLECTION",
         "fields": [
           { "fieldPath": "userId", "order": "ASCENDING" },
           { "fieldPath": "style_tags", "arrayConfig": "CONTAINS_ANY" }
         ]
       },
       {
         "collectionGroup": "wardrobe",
         "queryScope": "COLLECTION",
         "fields": [
           { "fieldPath": "userId", "order": "ASCENDING" },
           { "fieldPath": "material", "order": "ASCENDING" },
           { "fieldPath": "seasonality", "arrayConfig": "CONTAINS" }
         ]
       },
       {
         "collectionGroup": "outfits",
         "queryScope": "COLLECTION",
         "fields": [
           { "fieldPath": "user_id", "order": "ASCENDING" },
           { "fieldPath": "createdAt", "order": "ASCENDING" }
         ]
       },
       {
         "collectionGroup": "outfits",
         "queryScope": "COLLECTION",
         "fields": [
           { "fieldPath": "user_id", "order": "ASCENDING" },
           { "fieldPath": "wasSuccessful", "order": "ASCENDING" }
         ]
       }
     ],
     "fieldOverrides": []
   }
   ```

5. **Deploy indexes**:
   ```bash
   firebase deploy --only firestore:indexes
   ```

### Method 3: Direct Console Links

For quick access, you can use these direct links to create indexes in the Firebase Console:

1. **Wardrobe - User + Category + Seasonality**:
   ```
   https://console.firebase.google.com/project/[YOUR_PROJECT_ID]/firestore/indexes?collection_group=wardrobe
   ```

2. **Outfits - User + Creation Date**:
   ```
   https://console.firebase.google.com/project/[YOUR_PROJECT_ID]/firestore/indexes?collection_group=outfits
   ```

## Index Creation Time

- **Small collections** (< 1000 documents): 1-5 minutes
- **Medium collections** (1000-10000 documents): 5-15 minutes
- **Large collections** (> 10000 documents): 15-60 minutes

## Monitoring Index Status

1. **Check Index Status**:
   - Go to Firestore > Indexes tab
   - Look for "Building" status
   - Wait for "Enabled" status

2. **Monitor Index Usage**:
   - Check the "Usage" column
   - High usage indicates frequently used indexes

## Troubleshooting

### Common Issues

1. **Index Already Exists**:
   - Check if the index already exists
   - Delete and recreate if needed

2. **Field Type Mismatch**:
   - Ensure field types match your data
   - Check for string vs number mismatches

3. **Array Field Issues**:
   - Use "Array contains" for single value
   - Use "Array contains any" for multiple values

### Error Messages

- **"Missing index"**: Create the required composite index
- **"Invalid field path"**: Check field names in your data
- **"Index building failed"**: Check data consistency and retry

## Best Practices

1. **Create indexes incrementally**: Start with the most critical queries
2. **Monitor costs**: Indexes consume read/write operations
3. **Test queries**: Verify indexes work with your actual data
4. **Clean up unused indexes**: Remove indexes that are no longer needed

## Next Steps

After creating the indexes:

1. **Wait for index building** to complete
2. **Run the test suite** to verify index resolution
3. **Monitor query performance** in Firebase Console
4. **Optimize further** based on usage patterns

## Support

If you encounter issues:

1. Check the [Firestore documentation](https://firebase.google.com/docs/firestore/query-data/indexing)
2. Review the [Firebase Console](https://console.firebase.google.com) for detailed error messages
3. Check the [Firebase Status Page](https://status.firebase.google.com) for service issues 