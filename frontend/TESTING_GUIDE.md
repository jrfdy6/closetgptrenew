# 🧪 Frontend Testing Guide for Outfit Editing

## 🚀 **Quick Start Testing**

### **Option 1: Production Testing (Recommended)**
```bash
# Open the live application
open https://closetgpt-frontend.vercel.app/outfits
```

### **Option 2: Local Development Testing**
```bash
# Start local development server
npm run dev

# Open in browser
open http://localhost:3000/outfits
```

## 📋 **Manual Testing Checklist**

### **1. Basic Modal Functionality**
- [ ] **Open Modal**: Click edit button on any outfit card
- [ ] **Verify Data**: Check that form fields are populated correctly
- [ ] **Close Modal**: Click Cancel button - modal should close
- [ ] **Close Modal**: Click X button - modal should close
- [ ] **Close Modal**: Click outside modal - modal should close

### **2. Form Validation Testing**
- [ ] **Required Fields**: Clear outfit name → error should appear
- [ ] **Required Fields**: Clear occasion → error should appear  
- [ ] **Required Fields**: Clear style → error should appear
- [ ] **Item Validation**: Remove all items → error should appear
- [ ] **Fix Errors**: Fill in required fields → errors should clear

### **3. Item Selection Testing**
- [ ] **Expand Wardrobe**: Click "Show Items" button
- [ ] **Search Items**: Type in search box to filter items
- [ ] **Filter by Type**: Use dropdown to filter by item type
- [ ] **Add Items**: Click + button to add items to outfit
- [ ] **Remove Items**: Click X button to remove items
- [ ] **Item Limits**: Try adding more than 10 items (should be limited)

### **4. Data Validation Testing**
- [ ] **Valid Items**: Select items that exist in wardrobe → no errors
- [ ] **Invalid Items**: Select items not in wardrobe → error should appear
- [ ] **Visual Indicators**: Invalid items should be highlighted in red
- [ ] **Warning Banner**: Warning should appear for invalid items

### **5. Save Functionality Testing**
- [ ] **Make Changes**: Edit outfit details and items
- [ ] **Save Changes**: Click Save button → should show success
- [ ] **No Changes**: Don't make changes → Save button should be disabled
- [ ] **Unsaved Indicator**: "Unsaved Changes" should appear when editing
- [ ] **Form Reset**: After successful save, form should reset

### **6. Error Recovery Testing**
- [ ] **Network Error**: Simulate network failure during save
- [ ] **Error Message**: Error message should appear
- [ ] **Modal Stays Open**: Modal should remain open on error
- [ ] **Refresh Data**: Click "Refresh Data" button
- [ ] **Data Reset**: Form should reset to server data

## 🔧 **Browser DevTools Testing**

### **Console Testing**
```javascript
// Open browser console (F12) and run these commands:

// 1. Check if outfit editing components are loaded
console.log('OutfitEditModal:', window.OutfitEditModal);

// 2. Test form validation
const modal = document.querySelector('[data-testid="outfit-edit-modal"]');
console.log('Modal found:', !!modal);

// 3. Check for errors
console.log('Console errors:', window.console.errors || []);
```

### **Network Tab Testing**
1. **Open DevTools** → Network tab
2. **Open outfit edit modal**
3. **Make changes and save**
4. **Verify API calls**:
   - `PUT /api/outfits/{id}` - should be called
   - Response should be 200 OK
   - Check request payload

### **Elements Tab Testing**
1. **Inspect modal elements**
2. **Check form field values**
3. **Verify event handlers are attached**
4. **Test accessibility attributes**

## 🧪 **Automated Testing**

### **Run Jest Tests**
```bash
# Run all tests
npm test

# Run specific test file
npm test -- --testPathPattern=OutfitEditModal.test.tsx

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### **Test Results Interpretation**
- ✅ **Passed**: Component working correctly
- ❌ **Failed**: Check error messages for issues
- ⚠️ **Warnings**: Non-critical issues, functionality still works

## 🐛 **Common Issues & Solutions**

### **Issue: Modal doesn't open**
**Solution**: Check if outfit data exists and edit button is clicked

### **Issue: Form validation not working**
**Solution**: Check if required fields are properly marked

### **Issue: Items not loading**
**Solution**: Check wardrobe data and API connections

### **Issue: Save not working**
**Solution**: Check network requests and API responses

## 📊 **Performance Testing**

### **Load Time Testing**
1. **Open DevTools** → Performance tab
2. **Record** while opening modal
3. **Check** for slow operations
4. **Target**: Modal should open in < 500ms

### **Memory Testing**
1. **Open DevTools** → Memory tab
2. **Take snapshot** before opening modal
3. **Open and close modal** several times
4. **Take snapshot** after
5. **Check** for memory leaks

## 🎯 **Success Criteria**

### **Functional Requirements**
- [ ] Modal opens and closes correctly
- [ ] Form validation works
- [ ] Item selection works
- [ ] Save functionality works
- [ ] Error handling works

### **Performance Requirements**
- [ ] Modal opens in < 500ms
- [ ] No memory leaks
- [ ] Smooth animations
- [ ] Responsive design

### **User Experience Requirements**
- [ ] Intuitive interface
- [ ] Clear error messages
- [ ] Accessible design
- [ ] Mobile-friendly

## 🚨 **Troubleshooting**

### **If tests fail:**
1. Check console for errors
2. Verify API endpoints are working
3. Check network connectivity
4. Review component props and state

### **If modal doesn't work:**
1. Check if user is authenticated
2. Verify outfit data exists
3. Check for JavaScript errors
4. Test in different browsers

### **If save fails:**
1. Check network requests
2. Verify API responses
3. Check form validation
4. Test with different data

## 📝 **Test Data Setup**

### **Create Test Outfits**
1. **Generate outfits** using the generate page
2. **Create variety**: Different occasions, styles, items
3. **Test edge cases**: Empty outfits, many items, special characters

### **Test User Accounts**
1. **Create test account** with sample data
2. **Add wardrobe items** for testing
3. **Generate test outfits** for editing

---

**Happy Testing! 🎉**

For issues or questions, check the console logs and network requests in DevTools.
