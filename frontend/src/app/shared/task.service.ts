import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable, signal } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Observable, switchMap, takeWhile, tap, timer } from 'rxjs';



export type TaskStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface BaseTask {
  id: string;
  status: TaskStatus;
  progress: number; // 0 to 100
  result_id?: string; // ID of the generated exercise
  error_message?: string;
}

@Injectable({
  providedIn: 'root',
})
export class TaskService {
  private readonly endpoint = '/api/teacher';

  // Signal to track all active tasks in the UI globally if needed
  activeTasks = signal<BaseTask[]>([]);
  totalProgress = computed(() => {
    const sum = this.activeTasks().reduce((acc, task) => acc + task.progress, 0);
    return this.activeTasks().length > 0 ? Number((sum / this.activeTasks().length).toFixed(2)) : 0;
  })

  private snackBar = inject(MatSnackBar);
  private http = inject(HttpClient);

  /**
   * Starts polling for a specific task status.
   * @param taskId The ID returned by the initial POST request
   * @param interval Polling interval in milliseconds (default 5s)
   */
  pollTaskStatus(taskId: string, interval: number = 5000): Observable<BaseTask> {
    return timer(0, interval).pipe(
      switchMap(() => this.getTaskStatus(taskId)),
      tap(task => {
        this.updateTaskInList(task);
        if (task.status === 'COMPLETED') {
          this.snackBar.open($localize`Exercise ready!`, $localize`Close`, { duration: 5000 })
            .afterDismissed().subscribe(() => this.activeTasks.set(this.activeTasks().filter(t => t.id !== task.id)));
        } else if (task.status === 'FAILED') {
          this.snackBar.open($localize`Error: ${task.error_message}`, $localize`Close`, { duration: 7000 });
        }
      }),
      // Continue polling as long as the task is not finished
      takeWhile(task => this.isTaskRunning(task.status), true)
    );
  }

  getTaskStatus(taskId: string): Observable<BaseTask> {
    return this.http.get<BaseTask>(`${this.endpoint}/${taskId}`);
  }

  private isTaskRunning(status: TaskStatus): boolean {
    return status === 'PENDING' || status === 'RUNNING';
  }

  private updateTaskInList(task: BaseTask): void {
    const currentTasks = this.activeTasks();
    const index = currentTasks.findIndex(t => t.id === task.id);

    if (index !== -1) {
      // Update existing task
      const updatedTasks = [...currentTasks];
      updatedTasks[index] = task;
      this.activeTasks.set(updatedTasks);
    } else {
      // Add new task to tracking list
      this.activeTasks.set([...currentTasks, task]);
    }

    if (!this.isTaskRunning(task.status)) {
      setTimeout(() => {
        this.activeTasks.set(this.activeTasks().filter(t => t.id !== task.id));
      }, 10000);
    }
  }
}
