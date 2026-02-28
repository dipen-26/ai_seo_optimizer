const BASE_URL = "http://127.0.0.1:8000"; 
async function testAPI() { 
  const res = await fetch(BASE_URL); 
  const data = await res.json(); 
  console.log(data); 
} 
