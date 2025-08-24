/**
 * BK25 Conversation Memory
 * 
 * Simple, effective conversation and automation storage
 * No complex vector databases - just what actually works
 */

import sqlite3 from 'sqlite3';
import { promises as fs } from 'fs';
import path from 'path';

export class ConversationMemory {
  constructor(dbPath = './data/bk25.db') {
    this.dbPath = dbPath;
    this.db = null;
    this.initializeDatabase();
  }

  /**
   * Initialize SQLite database
   */
  async initializeDatabase() {
    try {
      // Ensure data directory exists
      const dataDir = path.dirname(this.dbPath);
      await fs.mkdir(dataDir, { recursive: true });

      // Open database connection
      this.db = new sqlite3.Database(this.dbPath);

      // Create tables
      await this.createTables();
      
      console.log('📚 BK25 memory initialized');
    } catch (error) {
      console.error('Database initialization error:', error);
    }
  }

  /**
   * Create database tables
   */
  async createTables() {
    return new Promise((resolve, reject) => {
      this.db.serialize(() => {
        // Conversations table
        this.db.run(`
          CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            context TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
          )
        `);

        // Automations table
        this.db.run(`
          CREATE TABLE IF NOT EXISTS automations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            description TEXT NOT NULL,
            script TEXT NOT NULL,
            documentation TEXT,
            filename TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            used_count INTEGER DEFAULT 0
          )
        `);

        // User patterns table (for learning)
        this.db.run(`
          CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            pattern_data TEXT NOT NULL,
            frequency INTEGER DEFAULT 1,
            last_used DATETIME DEFAULT CURRENT_TIMESTAMP
          )
        `, (err) => {
          if (err) reject(err);
          else resolve();
        });
      });
    });
  }

  /**
   * Add a message to conversation history
   */
  async addMessage(role, content, context = {}) {
    return new Promise((resolve, reject) => {
      const contextJson = JSON.stringify(context);
      
      this.db.run(
        'INSERT INTO conversations (role, content, context) VALUES (?, ?, ?)',
        [role, content, contextJson],
        function(err) {
          if (err) reject(err);
          else resolve(this.lastID);
        }
      );
    });
  }

  /**
   * Get recent messages for context
   */
  async getRecentMessages(limit = 10) {
    return new Promise((resolve, reject) => {
      this.db.all(
        'SELECT role, content, context, timestamp FROM conversations ORDER BY timestamp DESC LIMIT ?',
        [limit],
        (err, rows) => {
          if (err) reject(err);
          else {
            // Reverse to get chronological order
            const messages = rows.reverse().map(row => ({
              role: row.role,
              content: row.content,
              context: JSON.parse(row.context || '{}'),
              timestamp: row.timestamp
            }));
            resolve(messages);
          }
        }
      );
    });
  }

  /**
   * Store generated automation
   */
  async addAutomation(automation) {
    return new Promise((resolve, reject) => {
      this.db.run(
        `INSERT INTO automations 
         (platform, description, script, documentation, filename) 
         VALUES (?, ?, ?, ?, ?)`,
        [
          automation.platform,
          automation.description,
          automation.script,
          automation.documentation || '',
          automation.filename || ''
        ],
        function(err) {
          if (err) reject(err);
          else resolve(this.lastID);
        }
      );
    });
  }

  /**
   * Find similar automations (simple text matching for now)
   */
  async findSimilarAutomations(description, platform = null) {
    return new Promise((resolve, reject) => {
      let query = `
        SELECT * FROM automations 
        WHERE description LIKE ? 
      `;
      let params = [`%${description}%`];

      if (platform) {
        query += ' AND platform = ?';
        params.push(platform);
      }

      query += ' ORDER BY used_count DESC, created_at DESC LIMIT 5';

      this.db.all(query, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  /**
   * Increment usage count for an automation
   */
  async incrementAutomationUsage(automationId) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'UPDATE automations SET used_count = used_count + 1 WHERE id = ?',
        [automationId],
        function(err) {
          if (err) reject(err);
          else resolve(this.changes);
        }
      );
    });
  }

  /**
   * Store a learned pattern
   */
  async addPattern(patternType, patternData) {
    return new Promise((resolve, reject) => {
      // First, check if pattern already exists
      this.db.get(
        'SELECT id, frequency FROM patterns WHERE pattern_type = ? AND pattern_data = ?',
        [patternType, JSON.stringify(patternData)],
        (err, row) => {
          if (err) {
            reject(err);
            return;
          }

          if (row) {
            // Update existing pattern
            this.db.run(
              'UPDATE patterns SET frequency = frequency + 1, last_used = CURRENT_TIMESTAMP WHERE id = ?',
              [row.id],
              function(updateErr) {
                if (updateErr) reject(updateErr);
                else resolve(row.id);
              }
            );
          } else {
            // Insert new pattern
            this.db.run(
              'INSERT INTO patterns (pattern_type, pattern_data) VALUES (?, ?)',
              [patternType, JSON.stringify(patternData)],
              function(insertErr) {
                if (insertErr) reject(insertErr);
                else resolve(this.lastID);
              }
            );
          }
        }
      );
    });
  }

  /**
   * Get conversation statistics
   */
  async getStats() {
    return new Promise((resolve, reject) => {
      this.db.serialize(() => {
        const stats = {};

        // Count conversations
        this.db.get(
          'SELECT COUNT(*) as count FROM conversations',
          (err, row) => {
            if (err) {
              reject(err);
              return;
            }
            stats.totalMessages = row.count;

            // Count automations
            this.db.get(
              'SELECT COUNT(*) as count FROM automations',
              (err2, row2) => {
                if (err2) {
                  reject(err2);
                  return;
                }
                stats.totalAutomations = row2.count;

                // Get platform distribution
                this.db.all(
                  'SELECT platform, COUNT(*) as count FROM automations GROUP BY platform',
                  (err3, rows3) => {
                    if (err3) {
                      reject(err3);
                      return;
                    }
                    stats.platformDistribution = rows3.reduce((acc, row) => {
                      acc[row.platform] = row.count;
                      return acc;
                    }, {});

                    resolve(stats);
                  }
                );
              }
            );
          }
        );
      });
    });
  }

  /**
   * Close database connection
   */
  async close() {
    if (this.db) {
      return new Promise((resolve) => {
        this.db.close((err) => {
          if (err) console.error('Database close error:', err);
          resolve();
        });
      });
    }
  }
}
