import { useState } from "react";

export function useSemanticFlag() {
  const [semanticFlag, setSemanticFlag] = useState(false);
  
  return { 
    semanticFlag, 
    setSemanticFlag,
    toggleSemanticFlag: () => setSemanticFlag(!semanticFlag)
  };
}

// Usage example:
// const { semanticFlag, setSemanticFlag, toggleSemanticFlag } = useSemanticFlag();
// 
// const res = await fetch(`/api/outfits/debug-filter?semantic=${semanticFlag}`);
// const { outfits, debug } = await res.json();
