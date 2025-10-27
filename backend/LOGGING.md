# Logging Configuration

## Overview

The backend uses Python's built-in logging module with configurable log levels to reduce noise in production while maintaining detailed logs in development.

## Log Levels

- **DEBUG**: Detailed information for diagnosing problems (item-by-item scoring, internal state)
- **INFO**: General informational messages (service started, request processed)
- **WARNING**: Warning messages (deprecated features, potential issues)
- **ERROR**: Error messages (failed requests, exceptions)
- **CRITICAL**: Critical issues that prevent the application from running

## Configuration

### Environment Variable

Set the `LOG_LEVEL` environment variable to control logging verbosity:

```bash
# Development (verbose logging)
export LOG_LEVEL=INFO

# Production (reduced logging, recommended for Railway)
export LOG_LEVEL=WARNING
```

### Railway Configuration

To set the log level in Railway:

1. Go to your Railway project dashboard
2. Select your backend service
3. Click on "Variables" tab
4. Add a new variable:
   - **Name:** `LOG_LEVEL`
   - **Value:** `WARNING` (recommended for production)
5. Click "Add" and redeploy

### Default Behavior

- **Without `LOG_LEVEL` set:** Defaults to `INFO` level
- **With `LOG_LEVEL=WARNING`:** Only WARNING, ERROR, and CRITICAL messages are logged
- **With `LOG_LEVEL=DEBUG`:** All messages including detailed item scoring logs

## Recent Changes (Oct 27, 2025)

### Issue Fixed
The backend was logging 500+ messages per second due to excessive `logger.info` calls in the outfit scoring loop. This caused:
- Railway rate limiting (500 logs/sec limit)
- Increased costs
- Performance degradation
- Difficult debugging

### Solution
1. Changed all item-by-item scoring logs from `logger.info` to `logger.debug`
2. Added environment-based log level configuration
3. Recommended production setting: `LOG_LEVEL=WARNING`

### Affected Files
- `backend/src/services/robust_outfit_generation_service.py`: Item scoring logs
- `backend/app.py`: Root logging configuration
- `backend/src/core/config.py`: Settings with LOG_LEVEL support

### Impact
With `LOG_LEVEL=WARNING` in production:
- ✅ Reduces log volume by ~95%
- ✅ Eliminates repetitive item scoring logs
- ✅ Stays well under Railway's 500 logs/sec limit
- ✅ Maintains error and warning visibility
- ✅ Debug logs still available when needed

## Testing

### Local Development
```bash
# Test with DEBUG level (very verbose)
LOG_LEVEL=DEBUG python backend/app.py

# Test with INFO level (normal)
LOG_LEVEL=INFO python backend/app.py

# Test with WARNING level (production-like)
LOG_LEVEL=WARNING python backend/app.py
```

### Verify in Railway
After setting `LOG_LEVEL=WARNING`:
1. Monitor Railway logs
2. Should see significant reduction in log volume
3. Errors and warnings still visible
4. No item-by-item scoring logs

## Best Practices

1. **Production:** Always use `LOG_LEVEL=WARNING` or higher
2. **Staging:** Use `LOG_LEVEL=INFO` for more visibility
3. **Development:** Use `LOG_LEVEL=DEBUG` when debugging specific issues
4. **Never:** Leave DEBUG logging on in production (costs money, hits rate limits)

## Troubleshooting

### Too Many Logs
- Set `LOG_LEVEL=WARNING` or `ERROR`
- Check for accidental `logger.info` in tight loops
- Consider adding log sampling for high-frequency events

### Missing Important Logs
- Verify `LOG_LEVEL` is not set too high (ERROR/CRITICAL)
- Check if the log statement uses appropriate level
- Review Railway log filters

### Performance Issues
- High log volume can cause performance degradation
- Use `LOG_LEVEL=WARNING` in production
- Add conditional logging for expensive operations

