import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.visualization import plot_bloch_vector
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# Qiskit Runtime Serviceを初期化
service = QiskitRuntimeService()

# 最も空いている実機バックエンドを探す
backend = service.least_busy(operational=True, simulator=False)
print(f"使用するバックエンド: {backend.name}")

# 量子テレポーテーション回路の構築
qr = QuantumRegister(3, 'q')
crz = ClassicalRegister(1, 'crz') 
crx = ClassicalRegister(1, 'crx') 
qc = QuantumCircuit(qr, crz, crx)

# 初期状態
qc.rx(np.pi/2, 0)
qc.rz(np.pi/2, 0)
qc.barrier() 

# エンタングルメント
qc.h(1)
qc.cx(1, 2)
qc.barrier()

# ベル測定
qc.cx(0, 1)
qc.h(0)
qc.barrier()
qc.measure(0, crz)
qc.measure(1, crx)

# 補正操作 (動的回路)
with qc.if_test((crx, 1)):
    qc.x(2)
with qc.if_test((crz, 1)):
    qc.z(2)

# トモグラフィ回路の作成
qc_tomo = qc.copy()
cr_tomo = ClassicalRegister(1, 'tomo') 
qc_tomo.add_register(cr_tomo)

# 3軸（X, Y, Z）測定用回路
qc_x = qc_tomo.copy()
qc_y = qc_tomo.copy()
qc_z = qc_tomo.copy()

# X軸測定
qc_x.h(2)
qc_x.measure(2, cr_tomo)

# Y軸測定
qc_y.rz(-np.pi/2, 2) 
qc_y.h(2)
qc_y.measure(2, cr_tomo)

# Z軸そのまま測定
qc_z.measure(2, cr_tomo)

circuits = [qc_x, qc_y, qc_z]
transpiled_circuits = transpile(circuits, backend=backend)


shots = 4096 
sampler = Sampler(mode=backend)
sampler.options.default_shots = shots
job = sampler.run(transpiled_circuits)
print(f"ジョブを送信 ID: {job.job_id()}")

# 結果を待機して取得
result = job.result()

def get_expectation_val_v2(pub_result, shots):
    # 特定のレジスタ 'tomo' のカウントを取得
    # 結果は {'0': 200, '1': 300} のような辞書で返される
    data = pub_result.data.tomo.get_counts()
    
    shots_0 = data.get('0', 0)
    shots_1 = data.get('1', 0)
            
    # 期待値 <σ> = (N0 - N1) / (N0 + N1)
    return (shots_0 - shots_1) / shots

val_x = get_expectation_val_v2(result[0], shots)
val_y = get_expectation_val_v2(result[1], shots)
val_z = get_expectation_val_v2(result[2], shots)

print(f"実機測定結果 (各軸の期待値):")
print(f"<X> = {val_x:.3f}")
print(f"<Y> = {val_y:.3f}")
print(f"<Z> = {val_z:.3f}")

print("トモグラフィにより再構成されたボブの状態:")
plot_bloch_vector([val_x, val_y, val_z], title="Reconstructed State (Real Hardware)")
plt.show()