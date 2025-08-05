/**
 * Price Updater Test Suite
 * Tests the consolidated price updater functionality
 */

import { jest } from '@jest/globals';

// Mock Supabase client
const mockSupabase = {
  from: jest.fn().mockReturnThis(),
  select: jest.fn().mockReturnThis(),
  or: jest.fn().mockReturnThis(),
  limit: jest.fn().mockReturnThis(),
  update: jest.fn().mockReturnThis(),
  eq: jest.fn().mockReturnThis(),
  execute: jest.fn(),
};

// Mock environment variables
process.env.SUPABASE_URL = 'https://test.supabase.co';
process.env.SUPABASE_ANON_KEY = 'test_key';
process.env.AMAZON_ACCESS_KEY = 'test_amazon_key';
process.env.AMAZON_SECRET_KEY = 'test_amazon_secret';

describe('PriceUpdater', () => {
  let priceUpdater;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock the Supabase client
    jest.doMock('@supabase/supabase-js', () => ({
      createClient: jest.fn(() => mockSupabase),
    }));

    // Import the class after mocking
    const { PriceUpdater } = require('../api/price-updater.js');
    priceUpdater = new PriceUpdater();
  });

  describe('extractASINFromLink', () => {
    test('should extract ASIN from /dp/ URL', () => {
      const link = 'https://amazon.com/dp/B08XXXXX';
      const asin = priceUpdater.extractASINFromLink(link);
      expect(asin).toBe('B08XXXXX');
    });

    test('should extract ASIN from /gp/product/ URL', () => {
      const link = 'https://amazon.com/gp/product/B08XXXXX';
      const asin = priceUpdater.extractASINFromLink(link);
      expect(asin).toBe('B08XXXXX');
    });

    test('should return null for invalid link', () => {
      const link = 'https://amazon.com/invalid';
      const asin = priceUpdater.extractASINFromLink(link);
      expect(asin).toBeNull();
    });

    test('should return null for empty link', () => {
      const asin = priceUpdater.extractASINFromLink(null);
      expect(asin).toBeNull();
    });
  });

  describe('getItemsToUpdate', () => {
    test('should return items that need updates', async () => {
      const mockItems = [
        {
          id: 1,
          title: 'Test Book',
          price_status: 'error',
          price_fetch_attempts: 0,
        },
        {
          id: 2,
          title: 'Test Book 2',
          price_status: 'out_of_stock',
          price_fetch_attempts: 0,
        },
      ];

      mockSupabase.execute.mockResolvedValue({
        data: mockItems,
        error: null,
      });

      const items = await priceUpdater.getItemsToUpdate();
      
      expect(items).toHaveLength(2);
      expect(items[0].title).toBe('Test Book');
      expect(items[1].title).toBe('Test Book 2');
    });

    test('should skip items with too many failed attempts', async () => {
      const mockItems = [
        {
          id: 1,
          title: 'Test Book',
          price_status: 'error',
          price_fetch_attempts: 5, // Too many attempts
        },
      ];

      mockSupabase.execute.mockResolvedValue({
        data: mockItems,
        error: null,
      });

      const items = await priceUpdater.getItemsToUpdate();
      
      expect(items).toHaveLength(0);
    });
  });

  describe('fetchAmazonPrice', () => {
    test('should return error when credentials not configured', async () => {
      // Mock missing credentials
      delete process.env.AMAZON_ACCESS_KEY;
      
      const result = await priceUpdater.fetchAmazonPrice('B08XXXXX');
      
      expect(result.price).toBeNull();
      expect(result.error).toBe('Amazon API credentials not configured');
      expect(result.source).toBe('amazon_api_not_configured');
    });

    test('should handle API errors gracefully', async () => {
      // Mock API error
      priceUpdater.scrapeAmazonPrice = jest.fn().mockRejectedValue(
        new Error('API Error')
      );

      const result = await priceUpdater.fetchAmazonPrice('B08XXXXX');
      
      expect(result.price).toBeNull();
      expect(result.error).toBe('API Error');
      expect(result.source).toBe('amazon_api_error');
    });
  });

  describe('updateItemPrice', () => {
    test('should update item price successfully', async () => {
      const item = {
        id: 1,
        title: 'Test Book',
        price: 10.00,
      };

      const priceData = {
        price: 12.00,
        inStock: true,
        source: 'amazon_api',
      };

      mockSupabase.execute.mockResolvedValue({
        error: null,
      });

      const result = await priceUpdater.updateItemPrice(item, priceData);
      
      expect(result).toBe(true);
      expect(priceUpdater.stats.successfulUpdates).toBe(1);
      expect(priceUpdater.stats.priceChanges).toHaveLength(1);
    });

    test('should handle database errors', async () => {
      const item = {
        id: 1,
        title: 'Test Book',
        price: 10.00,
      };

      const priceData = {
        price: 12.00,
        inStock: true,
        source: 'amazon_api',
      };

      mockSupabase.execute.mockResolvedValue({
        error: new Error('Database error'),
      });

      const result = await priceUpdater.updateItemPrice(item, priceData);
      
      expect(result).toBe(false);
      expect(priceUpdater.stats.failedUpdates).toBe(1);
      expect(priceUpdater.stats.errors).toHaveLength(1);
    });
  });

  describe('run', () => {
    test('should return success when no items need updating', async () => {
      mockSupabase.execute.mockResolvedValue({
        data: [],
        error: null,
      });

      const result = await priceUpdater.run();
      
      expect(result.success).toBe(true);
      expect(result.message).toBe('No updates needed');
    });

    test('should process items and return results', async () => {
      const mockItems = [
        {
          id: 1,
          title: 'Test Book',
          price_status: 'error',
          price_fetch_attempts: 0,
          affiliate_link: 'https://amazon.com/dp/B08XXXXX',
        },
      ];

      mockSupabase.execute
        .mockResolvedValueOnce({
          data: mockItems,
          error: null,
        })
        .mockResolvedValueOnce({
          error: null,
        });

      const result = await priceUpdater.run();
      
      expect(result.success).toBeDefined();
      expect(result.stats).toBeDefined();
      expect(result.stats.totalItems).toBe(1);
    });
  });
}); 