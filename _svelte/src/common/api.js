async function get(url, params) {
    if (params == undefined) {
        return await fetch(url)
    } else {
        const qs = new URLSearchParams(params)
        return await fetch(url + '?' + qs)
    }
}

async function del(url) {
    return await fetch(url, { method: 'delete', headers: { "x-CSRFToken": window.csrf_token } })
}

async function post(url, data) {
    return await fetch(url, {
        method: 'post',
        headers: {
            "x-CSRFToken": window.csrf_token,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    })
}

async function put(url, data) {
    return await fetch(url, {
        method: 'put',
        headers: {
            "x-CSRFToken": window.csrf_token,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    })
}

// topics
export async function getTopicForProject(projectId) {
    const resp = await get('/forum/api/v1/utils/get_topic_for_project/', { project: projectId })
    return {
        ok: resp.ok,
        data: await resp.json()
    }
}

export async function createTopicForProject(projectId) {
    const resp = await post('/forum/api/v1/utils/create_topic_for_project/', { project: projectId })
    return {
        ok: resp.ok,
        data: await resp.json()
    }
}


// threads
export async function listThreads(filter) {
    const resp = await get('/forum/api/v1/threads/', filter)
    return {
        ok: resp.ok,
        data: await resp.json()
    }
}

export async function getThread(threadId) {
    const resp = await get(`/forum/api/v1/threads/${threadId}/`)
    return {
        ok: resp.ok,
        data: await resp.json()
    }
}

export async function createOrUpdateThread(thread) {
    let resp;
    if (thread.id) {
        resp = await put(`/forum/api/v1/threads/${thread.id}/`, thread)
    } else {
        resp = await post(`/forum/api/v1/threads/`, thread)
    }
    return {
        ok: resp.ok,
        data: await resp.json()
    }
}

export async function deleteThread(threadId) {
    const resp = await del(`/forum/api/v1/threads/${threadId}/`)
    return {
        ok: resp.ok
    }
}