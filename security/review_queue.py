"""
Submission Review Queue
Implements a queue system for reviewing user submissions before they affect live content.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List
import hashlib


class SubmissionReviewQueue:
    """
    Manages a queue of user submissions for review.
    
    This system helps prevent content poisoning by:
    - Tracking all user submissions
    - Flagging suspicious patterns (e.g., repeated similar submissions)
    - Requiring review for high-risk submissions
    - Maintaining submission history per IP/user
    """
    
    def __init__(self, db_connection=None):
        """Initialize the review queue."""
        self.db = db_connection
        self.in_memory_queue = []  # Fallback if no DB
        
    def add_submission(
        self, 
        ip_address: str,
        user_id: str,
        action: str,
        topic: str,
        content: str,
        sources: List[str],
        auto_approve: bool = False
    ) -> Dict:
        """
        Add a submission to the review queue.
        
        Args:
            ip_address: IP address of submitter
            user_id: User identifier
            action: Type of submission ('report', 'add_info')
            topic: Article topic
            content: Submission content
            sources: List of sources
            auto_approve: Whether to auto-approve (for trusted users)
            
        Returns:
            Dict with submission details including status and review flags
        """
        submission = {
            'id': hashlib.sha256(f"{ip_address}{datetime.utcnow().isoformat()}{content}".encode()).hexdigest()[:16],
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'user_id': user_id,
            'action': action,
            'topic': topic,
            'content': content,
            'sources': sources,
            'status': 'auto_approved' if auto_approve else 'pending',
            'flags': self._check_submission_flags(ip_address, user_id, content, topic),
        }
        
        # Log the submission
        logging.info(
            f"Submission queued - ID: {submission['id']}, "
            f"Action: {action}, Topic: {topic}, "
            f"Status: {submission['status']}, "
            f"Flags: {len(submission['flags'])}"
        )
        
        # Store submission (in-memory for now, can be extended to DB)
        self.in_memory_queue.append(submission)
        
        # If DB is available, store there too
        if self.db:
            self._store_submission_to_db(submission)
        
        return submission
    
    def _check_submission_flags(
        self,
        ip_address: str,
        user_id: str,
        content: str,
        topic: str
    ) -> List[str]:
        """
        Check for suspicious patterns that should flag a submission for review.
        
        Returns:
            List of flag reasons
        """
        flags = []
        
        # Check submission frequency from this IP
        recent_submissions = self._get_recent_submissions_by_ip(ip_address, hours=1)
        if len(recent_submissions) >= 5:
            flags.append("high_submission_frequency")
        
        # Check for similar content from same IP
        similar_count = sum(
            1 for sub in recent_submissions 
            if self._content_similarity(content, sub.get('content', '')) > 0.8
        )
        if similar_count >= 2:
            flags.append("duplicate_content")
        
        # Check for submissions to same topic
        topic_submissions = [
            sub for sub in recent_submissions 
            if sub.get('topic', '').lower() == topic.lower()
        ]
        if len(topic_submissions) >= 3:
            flags.append("topic_concentration")
        
        # Check content length (very short might be spam)
        if len(content.strip()) < 20:
            flags.append("short_content")
        
        # Check for excessive URLs in content (spam indicator)
        url_count = content.lower().count('http://') + content.lower().count('https://')
        if url_count > 3:
            flags.append("excessive_urls")
        
        return flags
    
    def _get_recent_submissions_by_ip(
        self,
        ip_address: str,
        hours: int = 1
    ) -> List[Dict]:
        """Get recent submissions from an IP address."""
        from datetime import timedelta
        
        cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        
        # Filter in-memory queue
        recent = [
            sub for sub in self.in_memory_queue
            if sub['ip_address'] == ip_address and sub['timestamp'] > cutoff_time
        ]
        
        return recent
    
    def _content_similarity(self, content1: str, content2: str) -> float:
        """
        Calculate simple similarity between two content strings.
        
        Returns:
            Similarity score from 0.0 to 1.0
        """
        if not content1 or not content2:
            return 0.0
        
        # Simple character-based similarity
        set1 = set(content1.lower().split())
        set2 = set(content2.lower().split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union)
    
    def _store_submission_to_db(self, submission: Dict):
        """Store submission to database (placeholder for future DB integration)."""
        # This would use the actual database connection
        # For now, just log that we would store it
        logging.debug(f"Would store submission {submission['id']} to database")
    
    def should_require_review(self, submission: Dict) -> bool:
        """
        Determine if a submission should require manual review.
        
        Args:
            submission: Submission dictionary from add_submission
            
        Returns:
            True if manual review is required
        """
        # Auto-approved submissions don't need review
        if submission['status'] == 'auto_approved':
            return False
        
        # Any flags trigger review requirement
        if len(submission['flags']) > 0:
            return True
        
        # Additional criteria could be added here
        # For example, submissions from new IPs, certain topics, etc.
        
        return False
    
    def get_pending_submissions(self, limit: int = 50) -> List[Dict]:
        """
        Get submissions pending review.
        
        Args:
            limit: Maximum number of submissions to return
            
        Returns:
            List of pending submissions
        """
        pending = [
            sub for sub in self.in_memory_queue
            if sub['status'] == 'pending'
        ]
        
        # Sort by timestamp, newest first
        pending.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return pending[:limit]
    
    def approve_submission(self, submission_id: str) -> bool:
        """
        Approve a submission.
        
        Args:
            submission_id: ID of submission to approve
            
        Returns:
            True if approved successfully
        """
        for sub in self.in_memory_queue:
            if sub['id'] == submission_id:
                sub['status'] = 'approved'
                sub['reviewed_at'] = datetime.utcnow().isoformat()
                logging.info(f"Submission {submission_id} approved")
                return True
        
        return False
    
    def reject_submission(self, submission_id: str, reason: str = "") -> bool:
        """
        Reject a submission.
        
        Args:
            submission_id: ID of submission to reject
            reason: Reason for rejection
            
        Returns:
            True if rejected successfully
        """
        for sub in self.in_memory_queue:
            if sub['id'] == submission_id:
                sub['status'] = 'rejected'
                sub['rejection_reason'] = reason
                sub['reviewed_at'] = datetime.utcnow().isoformat()
                logging.info(f"Submission {submission_id} rejected: {reason}")
                return True
        
        return False
    
    def get_submission_stats(self) -> Dict:
        """
        Get statistics about submissions.
        
        Returns:
            Dictionary with submission statistics
        """
        total = len(self.in_memory_queue)
        pending = sum(1 for sub in self.in_memory_queue if sub['status'] == 'pending')
        approved = sum(1 for sub in self.in_memory_queue if sub['status'] == 'approved')
        rejected = sum(1 for sub in self.in_memory_queue if sub['status'] == 'rejected')
        auto_approved = sum(1 for sub in self.in_memory_queue if sub['status'] == 'auto_approved')
        flagged = sum(1 for sub in self.in_memory_queue if len(sub['flags']) > 0)
        
        return {
            'total': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'auto_approved': auto_approved,
            'flagged': flagged
        }


# Global instance
_review_queue = None


def get_review_queue() -> SubmissionReviewQueue:
    """Get the global review queue instance."""
    global _review_queue
    if _review_queue is None:
        _review_queue = SubmissionReviewQueue()
    return _review_queue
