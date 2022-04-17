const followBtn = document.querySelector('a.follow')
followBtn.addEventListener('click', e => {
    e.preventDefault();
    fetch('{% url "user_follow" %}', {
       method : 'POST',
       headers: {'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest' },
        body: JSON.stringify({
            id: followBtn.dataset.id,
            action: followBtn.dataset.action
        })             
    }).then(response => response.json()).then(()=>{
        if (response['status'] == 'ok') {
            let previous_action = followBtn.dataset.action;
            // toggle data-action
            followBtn.dataset.action = (previous_action == 'follow' ? 'unfollow' : 'follow')
            // toggle link text
            followBtn.textContent = (previous_action == 'follow' ? 'unfollow' : 'follow')
            // update total followers
            const total = document.querySelector('span.count .total')
            let previous_followers = parseInt(total.textContent);
            total.textContent = (previous_action == 'follow' ? previous_followers + 1 : previous_followers - 1);
        }
    }).catch(error => {
        console.log(error)
    })
})