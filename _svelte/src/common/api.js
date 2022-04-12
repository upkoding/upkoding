async function get(url, params) {
    if (params == undefined) {
        return await fetch(url)
    } else {
        const qs = new URLSearchParams(params)
        return await fetch(url + '?' + qs)
    }
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

export const getTopicForProject = async (projectId) => {
    const resp = await get('/forum/api/v1/utils/get_topic_for_project/', { project: projectId })
    return resp.ok ? await resp.json() : null
}

export const createTopicForProject = async (projectId) => {
    const resp = await post('/forum/api/v1/utils/create_topic_for_project/', { project: projectId })
    return resp.ok ? await resp.json() : null
}

export const getTopicThreads = async (topicId) => {
    const resp = await get('/forum/api/v1/threads/', { topic: topicId })
    return resp.ok ? await resp.json() : null
}