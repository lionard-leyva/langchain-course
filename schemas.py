from  typing import List
from pydantic import BaseModel,Field


class Source(BaseModel): #herencia
    """Schema for the source by the agent"""

    url:str = Field(...,description="url of the source") #Descripcion requerida

class AgentResponse(BaseModel):
    """Schema for the response by the agent"""

    answer:str = Field(...,description="the answer of the agent to the query")
    sources:List[Source] = Field(
        default_factory=list, #se usa para listas, dicts, sets PARA VALORES INMUTABLES! CUANDO SE CREA AGENTRESPONSE SE CREARA NUEVA INSTACIA VACIA CASO CONTRATIO TENDRA LO MISMO TODOS
        description="the sources of the answer"
    )
