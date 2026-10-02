# UCE 核心组件 2：神经符号记忆图谱 (Neuro-Symbolic Memory Graph)
# 纯 Python 标准库，依赖于 vsa_engine.py
# 特性：融合 VSA 直觉检索与符号逻辑图遍历，实现记忆的"模糊联想 + 精确查询"

from vsa_engine import HyperVector

class MemoryGraph:
    def __init__(self):
        # 节点库：{node_id: {"name": str, "type": str, "vsa": HyperVector}}
        self.nodes = {}
        
        # 边库（关系）：{subject_id: [(relation, object_id), ...]}
        self.edges = {}
        
        # 问题-代码映射库：{problem_vsa: {"code": str, "ast": object, "similarity": float}}
        self.code_memory = []

    # ================= 节点管理 =================
    def add_node(self, name, node_type="concept"):
        """添加一个节点，并自动生成其超维向量"""
        if name in self.nodes:
            return name
        
        vsa_vector = HyperVector.random()
        self.nodes[name] = {
            "name": name,
            "type": node_type,
            "vsa": vsa_vector
        }
        if name not in self.edges:
            self.edges[name] = []
        return name

    def add_fact(self, subject, relation, object_):
        """
        添加一条事实关系（符号逻辑层）
        例如：add_fact("苹果", "属于", "水果")
        """
        self.add_node(subject)
        self.add_node(object_)
        
        # 在边的记录中保存关系（VSA置换可以用于表达关系）
        self.edges[subject].append((relation, object_))
        
        # 同时在 VSA 层面，将 subject 和 object 进行绑定
        # 这样可以通过 VSA 的相似度来"模糊联想"这条事实
        # 例如：苹果.bind(水果) 得到一个新的向量，存入节点的扩展信息
        pass

    # ================= 记忆检索 =================
    def query_logic(self, subject, relation=None):
        """
        精确逻辑查询：根据主语和关系，查出所有的宾语
        """
        if subject not in self.edges:
            return []
        
        results = []
        for rel, obj in self.edges[subject]:
            if relation is None or rel == relation:
                results.append(obj)
        return results

    def query_by_similarity(self, query_vsa, threshold=0.7, top_k=5):
        """
        模糊联想查询：根据一个 VSA 向量，找出记忆中最相似的概念
        """
        scored = []
        for name, data in self.nodes.items():
            sim = query_vsa.similarity(data["vsa"])
            if sim >= threshold:
                scored.append((sim, name))
        
        # 按相似度降序排序，返回前 top_k 个
        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[:top_k]

    # ================= 代码记忆 =================
    def store_code(self, problem_vsa, code_string, ast_object):
        """
        将成功通过进化生成的代码存入记忆库
        以后遇到类似问题，直接凭 VSA 相似度调出代码，无需再次进化
        """
        self.code_memory.append({
            "problem_vsa": problem_vsa,
            "code": code_string,
            "ast": ast_object
        })

    def recall_code(self, problem_vsa, threshold=0.85):
        """
        根据问题向量，回忆曾经写过的代码
        """
        best_match = None
        highest_sim = 0.0
        
        for record in self.code_memory:
            sim = problem_vsa.similarity(record["problem_vsa"])
            if sim > highest_sim:
                highest_sim = sim
                best_match = record
        
        if highest_sim >= threshold:
            return best_match
        
        return None

    # ================= 联网数据接入接口 =================
    def ingest_web_data(self, raw_text, source_url):
        """
        预留接口：将联网抓取到的非结构化文本，转化为超维向量并存入记忆。
        具体实现将在后续加联网功能时完成，目前只定义接口。
        """
        # 逻辑：将文本分词 -> 转化为超维向量 -> 建立新节点
        pass