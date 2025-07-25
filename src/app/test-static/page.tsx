export default function TestStatic() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: 'red' }}>STATIC TEST PAGE</h1>
      <p>If you can see this, Next.js routing is working.</p>
      <p>Static test page loaded successfully!</p>
      <div style={{ 
        backgroundColor: 'yellow', 
        padding: '10px', 
        margin: '10px 0',
        border: '2px solid red'
      }}>
        <strong>YELLOW BOX TEST</strong>
      </div>
    </div>
  );
} 