# Continuous Integration (CI) Setup

This document describes the comprehensive CI pipeline for ClosetGPT that automatically runs all tests on each commit.

## 🚀 CI Workflows

### 1. Complete CI Pipeline (`complete-ci.yml`)
**Triggers:** Push to main/develop, Pull Requests
**Runs:** All tests (Backend, Frontend, E2E)

### 2. Backend Tests (`backend-tests.yml`)
**Triggers:** Changes to backend code
**Runs:** Python unit tests, validation tests, security scans

### 3. Frontend Tests (`frontend-tests.yml`)
**Triggers:** Changes to frontend code
**Runs:** JavaScript/TypeScript tests, linting, build verification

### 4. Integration Tests (`integration-tests.yml`)
**Triggers:** Changes to both backend and frontend
**Runs:** API integration tests, E2E tests

### 5. Nightly Tests (`nightly-tests.yml`)
**Triggers:** Daily at 2 AM UTC, manual dispatch
**Runs:** Comprehensive test suite with extended coverage

## 📋 Test Categories

### Backend Tests
- ✅ **Unit Tests** - pytest with coverage reporting
- ✅ **Validation Tests** - Outfit validation orchestrator tests
- ✅ **Security Scans** - Bandit (code security) + Safety (dependencies)
- ✅ **Linting** - flake8, black, isort
- ✅ **Outfit Generation Tests** - API endpoint testing

### Frontend Tests
- ✅ **Unit Tests** - Jest/React Testing Library
- ✅ **Type Checking** - TypeScript compilation
- ✅ **Linting** - ESLint + Prettier
- ✅ **Build Verification** - Next.js build process
- ✅ **Dependency Audit** - npm audit for vulnerabilities

### E2E Tests
- ✅ **Cypress Tests** - Full user flow simulation
- ✅ **Validation Scenarios** - Soft/hard rule testing
- ✅ **Cross-browser Testing** - Chrome, Firefox, Safari
- ✅ **Performance Testing** - Response time validation

### Integration Tests
- ✅ **API Integration** - Backend-frontend communication
- ✅ **Database Integration** - PostgreSQL with test data
- ✅ **Service Integration** - All microservices working together

## 🔧 Setup Instructions

### Prerequisites
1. **GitHub Repository** with proper permissions
2. **Secrets configured** (if needed for external services)
3. **Branch protection rules** (recommended)

### Local Testing
Before pushing, run tests locally:

```bash
# Backend tests
cd backend
python run_validation_tests.py
python test_outfit_generation.py
pytest tests/ -v

# Frontend tests
cd frontend
npm test
npm run lint
npm run build
npx cypress run
```

### CI Configuration
The workflows are automatically configured to:
- Cache dependencies for faster builds
- Run tests in parallel where possible
- Generate comprehensive reports
- Upload artifacts for debugging
- Comment on PRs with test results

## 📊 Test Results & Reporting

### Coverage Reports
- **Backend:** Codecov integration with detailed coverage
- **Frontend:** Jest coverage reports
- **E2E:** Cypress video recordings and screenshots

### Security Reports
- **Bandit:** Python code security analysis
- **Safety:** Dependency vulnerability scanning
- **npm audit:** Node.js dependency security

### Performance Metrics
- **API Response Times:** Backend endpoint performance
- **Build Times:** Frontend compilation speed
- **Test Execution:** Overall test suite performance

## 🚨 Failure Handling

### Automatic Retries
- Failed tests are retried up to 2 times
- Network issues are handled gracefully
- Timeout configurations prevent hanging builds

### Error Reporting
- Detailed error logs in GitHub Actions
- Artifact uploads for debugging
- PR comments with test summaries

### Rollback Strategy
- Failed builds prevent deployment
- Previous working versions remain available
- Manual intervention for critical issues

## 📈 Monitoring & Alerts

### Success Metrics
- Test pass rate > 95%
- Coverage > 80%
- Build time < 10 minutes
- Zero security vulnerabilities

### Alert Conditions
- Test failures in main branch
- Security vulnerabilities detected
- Performance regressions
- Build time increases > 50%

## 🔄 Continuous Improvement

### Regular Updates
- Dependency updates (weekly)
- Security patches (immediate)
- Test coverage improvements (monthly)
- Performance optimizations (quarterly)

### Feedback Loop
- Test results inform development priorities
- Failed tests guide bug fixes
- Performance data drives optimizations
- Security findings trigger updates

## 🛠️ Troubleshooting

### Common Issues

1. **Tests failing locally but passing in CI**
   - Check environment differences
   - Verify dependency versions
   - Test with clean environment

2. **Slow build times**
   - Optimize dependency caching
   - Parallelize independent tests
   - Remove unnecessary steps

3. **Flaky tests**
   - Add retry logic
   - Improve test isolation
   - Fix timing dependencies

### Debug Commands

```bash
# Run specific test categories
npm run test:unit
npm run test:integration
npm run test:e2e

# Debug CI locally
act -j backend-tests
act -j frontend-tests

# Check test coverage
npm run test:coverage
python -m pytest --cov=src --cov-report=html
```

## 📚 Best Practices

### Code Quality
- Write tests for all new features
- Maintain > 80% code coverage
- Follow linting rules strictly
- Document complex test scenarios

### Performance
- Keep test execution under 10 minutes
- Use parallel execution where possible
- Cache dependencies effectively
- Monitor resource usage

### Security
- Regular dependency updates
- Automated security scanning
- Manual code reviews
- Vulnerability response plan

## 🎯 Success Criteria

A successful CI pipeline should:
- ✅ Catch regressions early
- ✅ Provide fast feedback (< 10 minutes)
- ✅ Maintain high test coverage
- ✅ Ensure code quality standards
- ✅ Prevent security vulnerabilities
- ✅ Support rapid development cycles

## 📞 Support

For CI-related issues:
1. Check GitHub Actions logs
2. Review test artifacts
3. Consult this documentation
4. Create issue with detailed context

---

**Last Updated:** July 2024
**Maintained by:** Development Team 