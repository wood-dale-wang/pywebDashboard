from typing import Any, Dict
from engine import WidgetBaseModule

class postTest(WidgetBaseModule):
    def __init__(self, settings):
        super().__init__(settings)

    async def get_data(self) -> dict[str, Any]:
        return {
            "html":"""<p id="formRes"></p>
<button id="subp" onclick="submitForm(event)">up</button>
""",
            "script":"""
console.log("eee");
document.getElementById('subp').addEventListener("click",
  (event) => {
    event.preventDefault(); // 阻止默认提交行为
    var pobj = document.querySelector('#formRes');
    fetch('http://localhost:8000/api/widget/postTest', { // 注意加上协议 http://
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'msg':'ok'})
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            pobj.innerHTML = JSON.stringify(data) // 确保 data 是字符串
        }).catch(error => console.error('Error:', error));
    });"""
        }
    
    async def post_data(self,require:dict[str, Any]) -> Dict[str, Any]:
        return require