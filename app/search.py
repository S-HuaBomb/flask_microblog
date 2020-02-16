from flask import current_app


def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)  # 获取 model.field (获取对象的属性)
    current_app.elasticsearch.index(index=index, doc_type=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query, page, per_page):
    """
    multi_match，它可以跨多个字段进行搜索。
    通过传递*的字段名称，我告诉Elasticsearch查看所有字段，
    所以基本上我就是搜索了整个索引

    :return:
        ids: 搜索命中的索引id列表
        search['hits']['total']: 搜索命中的条数(用于分页)
    """
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        doc_type=index,
        body={
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['*']
                }
            },
            'from': (page - 1) * per_page,
            'size': per_page
        }
    )
    ids = [int(hit['_id']) for hit in search['hits']['hits']]  # 搜索命中的索引的id们
    return ids, search['hits']['total']
