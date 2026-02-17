import os
import torch

def save_and_send_ckpt_to_worker(central_agent, wid, q, step, args):
    """
    Salva il checkpoint per il worker wid e rimuove il precedente.
    Il file precedente viene identificato come ckpt_step{step_prev}_w{wid}.pth
    dove step_prev è lo step immediatamente precedente inviato.
    """
    os.makedirs(args.log_dir, exist_ok=True)

    # ---- Nuovo checkpoint ----
    ckpt_path = os.path.join(args.log_dir, f"ckpt_step{step}_w{wid}.pth")

    # ---- Salvataggio checkpoint ----
    try:
        ckpt_obj = central_agent.checkpoint_attributes()
        torch.save(ckpt_obj, ckpt_path)
    except Exception:
        ckpt_obj = central_agent.checkpoint_attributes()
        torch.save(ckpt_obj, ckpt_path)

    # ---- Cancella il checkpoint precedente ----
    # Per i worker, sappiamo che gli step sono deterministici:
    # primi step = 0, poi = episode_count * train_every → sempre maggiori.
    # Quindi il precedente è semplicemente quello con lo step più alto < step.
    try:
        prefix = f"ckpt_step"
        suffix = f"_w{wid}.pth"

        # Scandisce la cartella alla ricerca di vecchi ckpt del worker
        for fname in os.listdir(args.log_dir):
            if fname.startswith(prefix) and fname.endswith(suffix):
                # Estrae lo step dal nome
                try:
                    old_step = int(fname[len(prefix): fname.index("_w")])
                except:
                    continue

                # Cancella solo quelli precedenti
                if old_step < step:
                    old_path = os.path.join(args.log_dir, fname)
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        print(f"Could not remove old checkpoint {old_path}: {e}")
    except Exception as e:
        print(f"Error while cleaning previous checkpoints: {e}")

    # ---- Invia ckpt al worker ----
    try:
        # svuota eventuale vecchio messaggio (non blocca)
        try:
            _ = q.get_nowait()
        except Exception:
            pass

        q.put(ckpt_path, block=True, timeout=2)
        return True

    except Exception as e:
        print(f"Could not send ckpt to worker queue: {e}")
        return False
