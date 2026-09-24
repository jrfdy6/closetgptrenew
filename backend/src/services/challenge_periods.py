"""UTC cadence windows for the existing recurring challenge catalog."""
from datetime import timedelta

def challenge_period(cadence, now):
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if cadence == 'daily':
        return '-' + now.date().isoformat(), midnight + timedelta(days=1)
    if cadence == 'weekly':
        year, week, _ = now.isocalendar()
        return f'-{year}-W{week:02d}', midnight + timedelta(days=7-now.weekday())
    if cadence in {'monthly', 'quarterly'}:
        quarter = (now.month-1)//3 + 1
        month = now.month+1 if cadence == 'monthly' else quarter*3+1
        end = midnight.replace(year=now.year + (month>12), month=1 if month>12 else month, day=1)
        return (f'-{now.year}-{now.month:02d}' if cadence=='monthly' else f'-{now.year}-Q{quarter}'), end
    return '', None


def completed_in_period(definition, records, now):
    """Honor migrated completion archives even when active tombstones are absent."""
    from datetime import datetime
    from .wear_projection import _ms
    suffix, _ = challenge_period(definition.cadence, now)
    for record in records:
        if record.get('challenge_id') != definition.id or record.get('status') != 'completed':
            continue
        if definition.cadence == 'always' or not definition.cadence:
            return True
        identity = record.get('instance_id')
        if identity and identity != definition.id:
            if identity == definition.id + suffix:
                return True
            continue
        stamp = record.get('started_at') or record.get('completed_at')
        if not stamp:
            return True  # Unknown legacy completion is not proof of an unpaid new period.
        completed = datetime.fromtimestamp(_ms(stamp)/1000, now.tzinfo)
        if challenge_period(definition.cadence, completed)[0] == suffix:
            return True
    return False
