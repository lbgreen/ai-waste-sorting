from dataclasses import dataclass
from typing import Optional

VALID = {"paper", "recycling", "general"}

@dataclass(frozen=True)
class Item:
    label: str
    confidence: float
    destination: Optional[str] = None
    unsupported: bool = False

@dataclass(frozen=True)
class Decision:
    status: str
    category: Optional[str] = None
    reason: str = ""


def assess(items, complete, empty, threshold):
    confirmed = {x.destination for x in items
                 if x.confidence >= threshold and x.destination in VALID}
    if len(confirmed) > 1:
        return Decision("ERROR_MIXED_WASTE", reason="Different confident disposal categories")
    if not complete:
        return Decision("WARNING_DETECTION", reason="Count, visibility or motion unresolved")
    if not items:
        return Decision("EMPTY" if empty else "WARNING_DETECTION")
    if any(x.unsupported for x in items):
        return Decision("ERROR_UNSUPPORTED", reason="Separate collection required")
    uncertain = [x.label for x in items
                 if x.confidence < threshold or x.destination not in VALID]
    if uncertain:
        return Decision("UNSURE", "general", "Uncertain: " + ", ".join(uncertain))
    return Decision("READY", next(iter(confirmed)), "Confirmed rule match")


class Gate:
    """Consecutive complete frames + fresh extra recheck; one event until empty."""
    def __init__(self, config):
        self.config = config
        self.latched = False
        self.last = None
        self.empty_since = None
        self.clear_candidate()

    def clear_candidate(self):
        self.signature = None
        self.since = None
        self.count = 0
        self.awaiting_recheck = False

    def fault(self):
        # A disconnect must not rearm an occupied presentation.
        self.latched = True
        self.empty_since = None
        self.clear_candidate()

    def update(self, decision, signature, now):
        if self.last is not None and (now <= self.last or now-self.last > self.config['max_gap_seconds']):
            self.clear_candidate()
            self.empty_since = None
        self.last = now
        if decision.status == 'EMPTY':
            self.clear_candidate()
            if self.empty_since is None:
                self.empty_since = now
            if now-self.empty_since >= self.config['empty_reset_seconds']:
                self.latched = False
            return decision, None
        self.empty_since = None
        if decision.status not in ('READY', 'UNSURE'):
            self.clear_candidate()
            return decision, None
        if self.latched:
            return Decision('LATCHED', decision.category, 'Clear the entire tray to rearm'), None
        key = (decision.status, decision.category, signature)
        if key != self.signature:
            self.clear_candidate()
            self.signature, self.since = key, now
        self.count += 1
        if self.awaiting_recheck:
            self.latched = True
            return decision, decision.category
        if (self.count >= self.config['stable_frames'] and
                now-self.since >= self.config['stable_seconds']):
            self.awaiting_recheck = True
        return Decision('OBSERVING', decision.category, decision.reason), None
