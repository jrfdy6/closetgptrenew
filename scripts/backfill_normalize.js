#!/usr/bin/env node
/**
 * Database Migration / Backfill Script for Semantic Filtering
 * Safely migrates existing wardrobe items to include normalized fields
 */

const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// Import normalization functions (assuming they're in lib/normalization.js)
const { normalizeItemMetadata } = require('../lib/normalization');

// Configuration
const BATCH_SIZE = 500;
const DRY_RUN = process.argv.includes('--dry-run');
const ENVIRONMENT = process.argv.includes('--production') ? 'production' : 'staging';

// Initialize Firebase Admin
if (!admin.apps.length) {
    const serviceAccount = require('../config/firebase-service-account.json');
    admin.initializeApp({
        credential: admin.credential.cert(serviceAccount)
    });
}

const db = admin.firestore();

// Statistics tracking
const stats = {
    totalProcessed: 0,
    totalUpdated: 0,
    totalSkipped: 0,
    totalErrors: 0,
    startTime: null,
    endTime: null
};

/**
 * Log statistics
 */
function logStats() {
    console.log(`📊 Backfill Stats: ${stats.totalProcessed} processed, ` +
                `${stats.totalUpdated} updated, ` +
                `${stats.totalSkipped} skipped, ` +
                `${stats.totalErrors} errors`);
}

/**
 * Get next batch of wardrobe items
 */
async function getNextBatch(cursor = null) {
    try {
        let query = db.collection('wardrobe')
            .orderBy('id')
            .limit(BATCH_SIZE);
        
        if (cursor) {
            query = query.startAfter({ id: cursor });
        }
        
        const snapshot = await query.get();
        const batch = [];
        
        snapshot.forEach(doc => {
            const itemData = doc.data();
            itemData.docId = doc.id;
            batch.push(itemData);
        });
        
        return batch;
        
    } catch (error) {
        console.error('❌ Error fetching batch:', error);
        return [];
    }
}

/**
 * Safely normalize item metadata
 */
function normalizeItemSafely(item) {
    try {
        // Check if already normalized
        if (item.normalized) {
            console.log(`⏭️  Item ${item.id || 'unknown'} already normalized, skipping`);
            return null;
        }
        
        // Normalize the item
        const normalized = normalizeItemMetadata(item);
        
        // Create normalized fields structure
        const normalizedFields = {
            style: normalized.style || [],
            occasion: normalized.occasion || [],
            mood: normalized.mood || [],
            season: normalized.season || [],
            normalizedAt: new Date().toISOString(),
            normalizedVersion: '1.0'
        };
        
        return normalizedFields;
        
    } catch (error) {
        console.error(`❌ Error normalizing item ${item.id || 'unknown'}:`, error);
        return null;
    }
}

/**
 * Update item with normalized fields
 */
async function updateItem(docId, normalizedFields) {
    try {
        if (DRY_RUN) {
            console.log(`🔍 DRY RUN: Would update ${docId} with normalized fields`);
            return true;
        }
        
        // Update the document with normalized fields
        await db.collection('wardrobe').doc(docId).update({
            normalized: normalizedFields
        });
        
        return true;
        
    } catch (error) {
        console.error(`❌ Error updating item ${docId}:`, error);
        return false;
    }
}

/**
 * Process a batch of items
 */
async function processBatch(batch) {
    const batchStats = {
        processed: 0,
        updated: 0,
        skipped: 0,
        errors: 0
    };
    
    for (const item of batch) {
        try {
            batchStats.processed++;
            stats.totalProcessed++;
            
            // Normalize the item
            const normalizedFields = normalizeItemSafely(item);
            
            if (normalizedFields === null) {
                batchStats.skipped++;
                stats.totalSkipped++;
                continue;
            }
            
            // Update the item
            const docId = item.docId;
            if (docId && await updateItem(docId, normalizedFields)) {
                batchStats.updated++;
                stats.totalUpdated++;
                console.log(`✅ Updated item ${item.id || 'unknown'}`);
            } else {
                batchStats.errors++;
                stats.totalErrors++;
            }
            
        } catch (error) {
            console.error(`❌ Error processing item ${item.id || 'unknown'}:`, error);
            batchStats.errors++;
            stats.totalErrors++;
        }
    }
    
    return batchStats;
}

/**
 * Run the complete backfill process
 */
async function runBackfill() {
    console.log(`🚀 Starting wardrobe backfill (batch_size: ${BATCH_SIZE}, dry_run: ${DRY_RUN})`);
    stats.startTime = new Date();
    
    let cursor = null;
    let batchNumber = 0;
    
    try {
        while (true) {
            batchNumber++;
            console.log(`📦 Processing batch ${batchNumber}...`);
            
            // Get next batch
            const batch = await getNextBatch(cursor);
            
            if (batch.length === 0) {
                console.log('✅ No more items to process');
                break;
            }
            
            // Process batch
            const batchStats = await processBatch(batch);
            
            // Log batch results
            console.log(`📊 Batch ${batchNumber} complete: ` +
                       `${batchStats.processed} processed, ` +
                       `${batchStats.updated} updated, ` +
                       `${batchStats.skipped} skipped, ` +
                       `${batchStats.errors} errors`);
            
            // Update cursor
            if (batch.length > 0) {
                cursor = batch[batch.length - 1].id;
            }
            
            // Log overall stats every 10 batches
            if (batchNumber % 10 === 0) {
                logStats();
            }
            
            // Small delay to avoid overwhelming the database
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
    } catch (error) {
        console.error('❌ Backfill failed:', error);
        throw error;
    } finally {
        stats.endTime = new Date();
        logFinalStats();
    }
}

/**
 * Log final statistics
 */
function logFinalStats() {
    const duration = stats.endTime - stats.startTime;
    
    console.log('='.repeat(60));
    console.log('📊 BACKFILL COMPLETE - FINAL STATISTICS');
    console.log('='.repeat(60));
    console.log(`⏱️  Duration: ${duration}ms`);
    console.log(`📦 Total processed: ${stats.totalProcessed}`);
    console.log(`✅ Total updated: ${stats.totalUpdated}`);
    console.log(`⏭️  Total skipped: ${stats.totalSkipped}`);
    console.log(`❌ Total errors: ${stats.totalErrors}`);
    
    if (stats.totalProcessed > 0) {
        const successRate = (stats.totalUpdated / stats.totalProcessed) * 100;
        console.log(`📈 Success rate: ${successRate.toFixed(1)}%`);
    }
    
    console.log('='.repeat(60));
    
    // Save stats to file
    const statsFile = `backfill_stats_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    fs.writeFileSync(statsFile, JSON.stringify(stats, null, 2));
    console.log(`💾 Stats saved to ${statsFile}`);
}

/**
 * Main function
 */
async function main() {
    // Environment safety check
    if (ENVIRONMENT === 'production' && !DRY_RUN) {
        const readline = require('readline');
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        
        const confirm = await new Promise(resolve => {
            rl.question('⚠️  You are about to run backfill on PRODUCTION. Are you sure? (yes/no): ', resolve);
        });
        
        rl.close();
        
        if (confirm.toLowerCase() !== 'yes') {
            console.log('❌ Production backfill cancelled');
            process.exit(1);
        }
    }
    
    try {
        await runBackfill();
        process.exit(0);
    } catch (error) {
        console.error('❌ Backfill failed:', error);
        process.exit(1);
    }
}

// Run the backfill
main();
