import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt


# qr[0]: Alice (転送したい状態)
# qr[1]: Alice (エンタングル用)
# qr[2]: Bob   (受け取り用)
qr = QuantumRegister(3, 'q')
# crz, crx: Aliceの測定結果を格納する古典ビット
crz = ClassicalRegister(1, 'crz') # Z測定用
crx = ClassicalRegister(1, 'crx') # X測定用
qc = QuantumCircuit(qr, crz, crx)

# 初期状態の作成
qc.rx(np.pi/2, 0)
qc.rz(np.pi/2, 0)
qc.barrier() 

# Aliceのq1とBobのq2をエンタングル
qc.h(1)
qc.cx(1, 2)
qc.barrier()

# ベル測定
qc.cx(0, 1)
qc.h(0)
qc.barrier()

# Aliceが測定して古典ビットに結果を入れる
qc.measure(0, crz)
qc.measure(1, crx)


# 古典通信の結果に基づいてBobが操作を行う
with qc.if_test((crx, 1)):
    qc.x(2)
with qc.if_test((crz, 1)):
    qc.z(2)


# トモグラフィ測定のための回路
from qiskit.visualization import plot_bloch_vector
qc_tomo = qc.copy()

cr_tomo = ClassicalRegister(1, 'tomo')
qc_tomo.add_register(cr_tomo)

# 3軸（X, Y, Z）それぞれの測定用回路を作成
qc_x = qc_tomo.copy()
qc_y = qc_tomo.copy()
qc_z = qc_tomo.copy()

# x軸測定
qc_x.h(2)
qc_x.measure(2, cr_tomo)

# Y軸測定
qc_y.rz(-np.pi/2, 2) 
qc_y.h(2)
qc_y.measure(2, cr_tomo)

# Z軸測定
qc_z.measure(2, cr_tomo)

# 実行
shots = 4096  # 試行回数
tomo_backend = AerSimulator() 
result_x = tomo_backend.run(qc_x, shots=shots).result()
result_y = tomo_backend.run(qc_y, shots=shots).result()
result_z = tomo_backend.run(qc_z, shots=shots).result()


def get_expectation_val(counts, shots):
    # 0が出た回数と1が出た回数から期待値を計算
    shots_0 = 0
    shots_1 = 0
    
    for key, val in counts.items():
        # キーの空白除去と最上位ビットの取得
        key_clean = key.replace(" ", "")
        bob_val = key_clean[0] 
        
        if bob_val == '0':
            shots_0 += val
        else:
            shots_1 += val
            
    # 期待値 <σ> = (N0 - N1) / (N0 + N1)
    return (shots_0 - shots_1) / shots

# 5. 各軸の期待値を計算
val_x = get_expectation_val(result_x.get_counts(), shots)
val_y = get_expectation_val(result_y.get_counts(), shots)
val_z = get_expectation_val(result_z.get_counts(), shots)

print(f"測定結果 (各軸の期待値):")
print(f"<X> = {val_x:.3f}")
print(f"<Y> = {val_y:.3f}")
print(f"<Z> = {val_z:.3f}")

# 6. 再構成された状態をブロック球に描画
print("トモグラフィにより再構成されたボブの状態:")
plot_bloch_vector([val_x, val_y, val_z], title="Reconstructed State (Tomography)")
plt.show()