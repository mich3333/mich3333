#!/usr/bin/env python3
"""
Memory Analytics System for Autonomous Claude.
Provides statistics, health monitoring, pattern detection, and insights.
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict
import statistics
import math

try:
    from memory import short_term, long_term, SHORT_TERM_DB
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("⚠ Warning: memory module not available")


class MemoryStatistics:
    """Calculate statistics about memory usage and distribution."""

    def __init__(self):
        self.short_term = short_term if MEMORY_AVAILABLE else None
        self.long_term = long_term if MEMORY_AVAILABLE else None

    def get_overview(self) -> Dict:
        """Get high-level overview of memory system."""
        if not MEMORY_AVAILABLE:
            return {"error": "Memory system not available"}

        short_term_count = self._get_short_term_count()
        long_term_count = self._get_long_term_count()

        return {
            "total_memories": short_term_count + long_term_count,
            "short_term_count": short_term_count,
            "long_term_count": long_term_count,
            "short_term_capacity": 50,
            "short_term_usage_percent": (short_term_count / 50) * 100,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_type_distribution(self) -> Dict[str, int]:
        """Get distribution of memory types."""
        if not MEMORY_AVAILABLE:
            return {}

        try:
            memories = self.short_term.get_recent(50)
            type_counts = Counter(m['type'] for m in memories)
            return dict(type_counts)
        except Exception as e:
            print(f"Error getting type distribution: {e}")
            return {}

    def get_temporal_distribution(self, hours: int = 24) -> List[Dict]:
        """Get memory creation distribution over time."""
        if not MEMORY_AVAILABLE:
            return []

        try:
            conn = sqlite3.connect(SHORT_TERM_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

            cursor.execute("""
                SELECT
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                    COUNT(*) as count,
                    type
                FROM memories
                WHERE timestamp >= ?
                GROUP BY hour, type
                ORDER BY hour ASC
            """, (cutoff,))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return results
        except Exception as e:
            print(f"Error getting temporal distribution: {e}")
            return []

    def get_storage_stats(self) -> Dict:
        """Get storage usage statistics."""
        if not MEMORY_AVAILABLE:
            return {}

        try:
            import os

            stats = {
                "database_path": SHORT_TERM_DB,
                "database_exists": os.path.exists(SHORT_TERM_DB) if SHORT_TERM_DB != ':memory:' else True,
                "database_size_bytes": 0,
                "database_size_kb": 0,
                "database_size_mb": 0
            }

            if SHORT_TERM_DB != ':memory:' and os.path.exists(SHORT_TERM_DB):
                size_bytes = os.path.getsize(SHORT_TERM_DB)
                stats["database_size_bytes"] = size_bytes
                stats["database_size_kb"] = round(size_bytes / 1024, 2)
                stats["database_size_mb"] = round(size_bytes / (1024 * 1024), 2)

            return stats
        except Exception as e:
            print(f"Error getting storage stats: {e}")
            return {}

    def _get_short_term_count(self) -> int:
        """Get count of short-term memories."""
        try:
            memories = self.short_term.get_recent(50)
            return len(memories)
        except:
            return 0

    def _get_long_term_count(self) -> int:
        """Get count of long-term memories."""
        if not self.long_term or not self.long_term.qdrant_available:
            return 0

        try:
            # Try to get collection info from Qdrant
            collection_info = self.long_term.client.get_collection(self.long_term.collection)
            return collection_info.points_count
        except:
            return 0


class HealthMonitor:
    """Monitor memory system health and performance."""

    def __init__(self):
        self.short_term = short_term if MEMORY_AVAILABLE else None
        self.long_term = long_term if MEMORY_AVAILABLE else None

    def get_health_score(self) -> Dict:
        """Calculate overall health score (0-100)."""
        if not MEMORY_AVAILABLE:
            return {"score": 0, "status": "unavailable", "issues": ["Memory system not available"]}

        scores = []
        issues = []

        # Check 1: Database connectivity (30 points)
        db_score, db_issues = self._check_database_health()
        scores.append(db_score)
        issues.extend(db_issues)

        # Check 2: Memory capacity (20 points)
        capacity_score, capacity_issues = self._check_capacity()
        scores.append(capacity_score)
        issues.extend(capacity_issues)

        # Check 3: Query performance (25 points)
        perf_score, perf_issues = self._check_performance()
        scores.append(perf_score)
        issues.extend(perf_issues)

        # Check 4: Data quality (25 points)
        quality_score, quality_issues = self._check_data_quality()
        scores.append(quality_score)
        issues.extend(quality_issues)

        # Calculate weighted average
        total_score = sum(scores)

        # Determine status
        if total_score >= 90:
            status = "excellent"
        elif total_score >= 75:
            status = "good"
        elif total_score >= 50:
            status = "fair"
        else:
            status = "poor"

        return {
            "score": round(total_score, 1),
            "status": status,
            "issues": issues,
            "checks": {
                "database": db_score,
                "capacity": capacity_score,
                "performance": perf_score,
                "data_quality": quality_score
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    def _check_database_health(self) -> Tuple[float, List[str]]:
        """Check database connectivity and integrity."""
        score = 30.0
        issues = []

        try:
            # Test short-term database
            conn = sqlite3.connect(SHORT_TERM_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            cursor.fetchone()
            conn.close()
        except Exception as e:
            score -= 15
            issues.append(f"Short-term database issue: {str(e)[:50]}")

        # Test long-term database
        if self.long_term and self.long_term.qdrant_available:
            try:
                self.long_term.client.get_collections()
            except Exception as e:
                score -= 15
                issues.append(f"Long-term database issue: {str(e)[:50]}")
        else:
            score -= 15
            issues.append("Long-term memory (Qdrant) not available")

        return score, issues

    def _check_capacity(self) -> Tuple[float, List[str]]:
        """Check memory capacity usage."""
        score = 20.0
        issues = []

        try:
            stats = MemoryStatistics()
            overview = stats.get_overview()
            usage = overview.get('short_term_usage_percent', 0)

            if usage >= 100:
                score -= 10
                issues.append("Short-term memory at full capacity")
            elif usage >= 90:
                score -= 5
                issues.append(f"Short-term memory almost full ({usage:.0f}%)")
            elif usage >= 75:
                score -= 2
                issues.append(f"Short-term memory usage high ({usage:.0f}%)")
        except Exception as e:
            score -= 10
            issues.append(f"Cannot check capacity: {str(e)[:50]}")

        return score, issues

    def _check_performance(self) -> Tuple[float, List[str]]:
        """Check query performance."""
        score = 25.0
        issues = []

        try:
            import time

            # Test query speed
            start = time.time()
            self.short_term.get_recent(10)
            query_time = time.time() - start

            if query_time > 0.5:
                score -= 15
                issues.append(f"Slow query performance ({query_time:.2f}s)")
            elif query_time > 0.1:
                score -= 5
                issues.append(f"Query performance could be better ({query_time:.2f}s)")
        except Exception as e:
            score -= 10
            issues.append(f"Cannot test performance: {str(e)[:50]}")

        return score, issues

    def _check_data_quality(self) -> Tuple[float, List[str]]:
        """Check data quality and integrity."""
        score = 25.0
        issues = []

        try:
            memories = self.short_term.get_recent(50)

            if not memories:
                score -= 10
                issues.append("No memories found")
                return score, issues

            # Check for empty content
            empty_count = sum(1 for m in memories if not m.get('content', '').strip())
            if empty_count > 0:
                score -= min(10, empty_count * 2)
                issues.append(f"{empty_count} memories with empty content")

            # Check for very short content
            short_count = sum(1 for m in memories if len(m.get('content', '')) < 10)
            if short_count > len(memories) * 0.5:
                score -= 5
                issues.append(f"Many memories with very short content ({short_count})")

            # Check timestamp validity
            invalid_ts = 0
            for m in memories:
                try:
                    datetime.fromisoformat(m['timestamp'])
                except:
                    invalid_ts += 1

            if invalid_ts > 0:
                score -= min(10, invalid_ts * 2)
                issues.append(f"{invalid_ts} memories with invalid timestamps")

        except Exception as e:
            score -= 10
            issues.append(f"Cannot check data quality: {str(e)[:50]}")

        return score, issues


class PatternDetector:
    """Detect patterns and trends in memory usage."""

    def __init__(self):
        self.short_term = short_term if MEMORY_AVAILABLE else None

    def detect_patterns(self) -> Dict:
        """Detect various patterns in memory data."""
        if not MEMORY_AVAILABLE:
            return {}

        try:
            memories = self.short_term.get_recent(50)

            if not memories:
                return {"patterns": [], "message": "Not enough data"}

            patterns = {
                "most_common_type": self._find_most_common_type(memories),
                "activity_pattern": self._analyze_activity_pattern(memories),
                "content_patterns": self._analyze_content_patterns(memories),
                "temporal_patterns": self._analyze_temporal_patterns(memories)
            }

            return patterns
        except Exception as e:
            return {"error": str(e)}

    def _find_most_common_type(self, memories: List[Dict]) -> Dict:
        """Find most common memory type."""
        type_counts = Counter(m['type'] for m in memories)
        if not type_counts:
            return {}

        most_common = type_counts.most_common(1)[0]
        total = sum(type_counts.values())

        return {
            "type": most_common[0],
            "count": most_common[1],
            "percentage": round((most_common[1] / total) * 100, 1)
        }

    def _analyze_activity_pattern(self, memories: List[Dict]) -> Dict:
        """Analyze when memories are created."""
        try:
            timestamps = [datetime.fromisoformat(m['timestamp']) for m in memories]
            hours = [t.hour for t in timestamps]

            hour_counts = Counter(hours)
            peak_hour = hour_counts.most_common(1)[0][0] if hour_counts else 0

            return {
                "peak_hour": peak_hour,
                "peak_hour_formatted": f"{peak_hour:02d}:00",
                "activity_distribution": dict(hour_counts)
            }
        except Exception as e:
            return {"error": str(e)}

    def _analyze_content_patterns(self, memories: List[Dict]) -> Dict:
        """Analyze content patterns."""
        try:
            contents = [m.get('content', '') for m in memories]

            # Calculate average length
            avg_length = statistics.mean(len(c) for c in contents) if contents else 0

            # Find common words (simple approach)
            all_words = []
            for content in contents:
                words = content.lower().split()
                all_words.extend(w for w in words if len(w) > 3)

            common_words = Counter(all_words).most_common(5)

            return {
                "average_content_length": round(avg_length, 1),
                "common_keywords": [word for word, count in common_words],
                "total_words": len(all_words)
            }
        except Exception as e:
            return {"error": str(e)}

    def _analyze_temporal_patterns(self, memories: List[Dict]) -> Dict:
        """Analyze temporal patterns."""
        try:
            timestamps = [datetime.fromisoformat(m['timestamp']) for m in memories]

            if len(timestamps) < 2:
                return {"message": "Not enough data"}

            # Calculate time gaps between memories
            timestamps.sort()
            gaps = [(timestamps[i+1] - timestamps[i]).total_seconds()
                   for i in range(len(timestamps)-1)]

            avg_gap = statistics.mean(gaps) if gaps else 0

            # Determine creation rate
            time_span = (timestamps[-1] - timestamps[0]).total_seconds()
            rate_per_hour = (len(memories) / time_span * 3600) if time_span > 0 else 0

            return {
                "average_gap_seconds": round(avg_gap, 1),
                "creation_rate_per_hour": round(rate_per_hour, 2),
                "time_span_hours": round(time_span / 3600, 2)
            }
        except Exception as e:
            return {"error": str(e)}


class InsightGenerator:
    """Generate insights and recommendations."""

    def __init__(self):
        self.stats = MemoryStatistics()
        self.health = HealthMonitor()
        self.patterns = PatternDetector()

    def generate_insights(self) -> Dict:
        """Generate actionable insights."""
        insights = []
        recommendations = []

        # Get data
        overview = self.stats.get_overview()
        health = self.health.get_health_score()
        patterns = self.patterns.detect_patterns()

        # Insight 1: Memory usage
        usage = overview.get('short_term_usage_percent', 0)
        if usage >= 90:
            insights.append({
                "type": "warning",
                "title": "High Memory Usage",
                "description": f"Short-term memory is {usage:.0f}% full",
                "severity": "high"
            })
            recommendations.append("Consider increasing memory capacity or archiving old memories")
        elif usage >= 75:
            insights.append({
                "type": "info",
                "title": "Memory Usage Growing",
                "description": f"Short-term memory is {usage:.0f}% full",
                "severity": "medium"
            })

        # Insight 2: Health issues
        if health['score'] < 75:
            insights.append({
                "type": "warning",
                "title": "Health Issues Detected",
                "description": f"System health score is {health['score']}/100",
                "severity": "high" if health['score'] < 50 else "medium"
            })
            recommendations.extend([f"Address: {issue}" for issue in health['issues'][:3]])

        # Insight 3: Long-term memory not available
        if overview.get('long_term_count', 0) == 0:
            insights.append({
                "type": "info",
                "title": "Long-term Memory Inactive",
                "description": "Qdrant vector database is not available",
                "severity": "low"
            })
            recommendations.append("Start Qdrant to enable semantic search and long-term memory")

        # Insight 4: Memory patterns
        most_common = patterns.get('most_common_type', {})
        if most_common and most_common.get('percentage', 0) > 70:
            insights.append({
                "type": "info",
                "title": "Dominant Memory Type",
                "description": f"{most_common.get('percentage', 0):.0f}% of memories are '{most_common.get('type')}'",
                "severity": "low"
            })
            recommendations.append("Consider diversifying memory types for better learning")

        # Insight 5: Content quality
        content_patterns = patterns.get('content_patterns', {})
        avg_length = content_patterns.get('average_content_length', 0)
        if avg_length < 20:
            insights.append({
                "type": "info",
                "title": "Short Memory Content",
                "description": f"Average memory length is only {avg_length:.0f} characters",
                "severity": "low"
            })
            recommendations.append("Consider adding more detailed content to memories")

        return {
            "insights": insights,
            "recommendations": recommendations,
            "summary": {
                "total_insights": len(insights),
                "high_severity": sum(1 for i in insights if i.get('severity') == 'high'),
                "medium_severity": sum(1 for i in insights if i.get('severity') == 'medium'),
                "low_severity": sum(1 for i in insights if i.get('severity') == 'low')
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instances
stats = MemoryStatistics()
health_monitor = HealthMonitor()
pattern_detector = PatternDetector()
insight_generator = InsightGenerator()


if __name__ == "__main__":
    print("🔍 Memory Analytics System\n")

    # Test statistics
    print("📊 Statistics:")
    overview = stats.get_overview()
    print(f"  Total memories: {overview['total_memories']}")
    print(f"  Short-term: {overview['short_term_count']}/50 ({overview['short_term_usage_percent']:.0f}%)")
    print(f"  Long-term: {overview['long_term_count']}")

    print("\n📈 Type Distribution:")
    type_dist = stats.get_type_distribution()
    for mem_type, count in type_dist.items():
        print(f"  {mem_type}: {count}")

    # Test health
    print("\n🏥 Health Check:")
    health = health_monitor.get_health_score()
    print(f"  Score: {health['score']}/100 ({health['status']})")
    if health['issues']:
        print("  Issues:")
        for issue in health['issues']:
            print(f"    - {issue}")

    # Test patterns
    print("\n🔎 Patterns:")
    patterns = pattern_detector.detect_patterns()
    most_common = patterns.get('most_common_type', {})
    if most_common:
        print(f"  Most common type: {most_common.get('type')} ({most_common.get('percentage')}%)")

    # Test insights
    print("\n💡 Insights:")
    insights_data = insight_generator.generate_insights()
    for insight in insights_data['insights'][:3]:
        print(f"  [{insight['severity']}] {insight['title']}: {insight['description']}")

    print("\n✅ Analytics system test complete!")
