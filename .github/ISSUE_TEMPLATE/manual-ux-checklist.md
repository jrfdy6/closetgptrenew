---
name: Manual/UX Testing Checklist
about: Use this template to track manual testing and UX validation for releases
title: "[MANUAL TEST] Release Testing Checklist"
labels: ["manual-testing", "ux", "release"]
assignees: ""
---

## Manual/UX Testing Checklist

### Pre-Release Testing
- [ ] All automated tests pass
- [ ] No critical security vulnerabilities
- [ ] Performance benchmarks meet requirements

### Onboarding Flow
- [ ] New user can sign up without errors
- [ ] Email verification works correctly
- [ ] Onboarding steps are clear and intuitive
- [ ] First outfit generated is appropriate and appealing
- [ ] User can complete onboarding in under 5 minutes

### Core Functionality
- [ ] Outfit generation works for all occasions (casual, formal, business, athletic)
- [ ] Outfits match selected style preferences
- [ ] Weather integration works correctly
- [ ] Wardrobe upload and management functions properly
- [ ] User can save and favorite outfits

### Mobile Experience
- [ ] App works smoothly on iOS Safari
- [ ] App works smoothly on Android Chrome
- [ ] All buttons and interactions are touch-friendly
- [ ] No horizontal scrolling issues
- [ ] Images load properly on mobile networks

### Edge Cases
- [ ] Empty wardrobe shows helpful guidance
- [ ] Invalid image uploads are handled gracefully
- [ ] Network errors show appropriate messages
- [ ] User can recover from errors without losing data
- [ ] App works with slow internet connections

### Visual Polish
- [ ] All images are high quality and load quickly
- [ ] Color scheme is consistent throughout
- [ ] Typography is readable on all devices
- [ ] Loading states are smooth and informative
- [ ] No obvious visual bugs or layout issues

### Performance
- [ ] App loads in under 3 seconds on mobile
- [ ] Outfit generation completes in under 10 seconds
- [ ] No memory leaks or performance degradation
- [ ] Smooth scrolling and animations

### Accessibility
- [ ] All interactive elements are keyboard accessible
- [ ] Color contrast meets WCAG guidelines
- [ ] Screen readers can navigate the app
- [ ] Text is resizable without breaking layout

## Issues Found
<!-- List any issues discovered during testing -->

### Critical Issues (Block Release)
- [ ] 

### Major Issues (Should Fix Soon)
- [ ] 

### Minor Issues (Nice to Have)
- [ ] 

## Recommendations
<!-- Any suggestions for improvements -->

## Tester Information
- **Tester Name:**
- **Device(s) Used:**
- **Browser(s) Used:**
- **Testing Date:**
- **Release Version:**

## Sign-off
- [ ] All critical issues resolved
- [ ] All major issues documented
- [ ] Ready for release 