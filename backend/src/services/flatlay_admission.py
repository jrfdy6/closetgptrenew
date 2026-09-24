"""One rollout-pause interpretation for saved projections and paid admission."""
import os

PAUSE_REASON = 'Flat-lay requests are temporarily paused. No credit was used. Please try again shortly.'


def flatlay_admission_state():
    value = os.environ.get('EASYOUTFIT_FLATLAY_REQUESTS_PAUSED', 'false').strip().lower()
    paused = value not in {'false', '0', 'no', 'off'}
    return {'flat_lay_admission_paused': paused,
            'flat_lay_admission_reason': PAUSE_REASON if paused else None}
