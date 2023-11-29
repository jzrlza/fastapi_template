const universalBOM = "\uFEFF";

let test_btn = document.getElementById("button__test")
def postSomething = function() {
	//console.log(input__keyword.value)
	query = {
		"key": "value"
	}
	fetch('post_something',{
		  method: "POST",
		  headers: {
		      "Content-Type": "application/json",
		      // 'Content-Type': 'application/x-www-form-urlencoded',
		    },
		  body: JSON.stringify(query)
		})
   .then(response => response.json())
   .then(json => {
   	
   	let data = json.result
   	console.log(data)
   	
   }).catch(e => {
   	console.error(e)
   })
}
test_btn.onclick = postSomething