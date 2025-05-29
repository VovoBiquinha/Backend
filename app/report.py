from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

async def get_database(request: Request) -> AsyncIOMotorDatabase:
    return request.app.mongodb

@router.get("/report/{student_id}")
async def generate_report(student_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        student = await db.New_Students.find_one({"_id": ObjectId(student_id)})
        if not student:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ID inválido: {e}")

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Relatório do aluno: {student_id}")
    p.drawString(100, 780, f"Escola: {student.get('school', '')}")
    p.drawString(100, 760, f"Endereço: {student.get('address', '')}")
    p.drawString(100, 740, f"Serviços: {student.get('services', '')}")
    p.drawString(100, 720, f"Diagnóstico: {student.get('diagnosis', '')}")
    p.drawString(100, 700, f"Uso de medicamento: {'Sim' if student.get('medication_usage', False) else 'Não'}")
    p.drawString(100, 680, f"Nome do medicamento: {student.get('medication_name', '')}")
    p.drawString(100, 660, f"Posologia: {student.get('dosage', '')}")

    p.showPage()
    p.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=relatorio_aluno_{student_id}.pdf"},
    )
