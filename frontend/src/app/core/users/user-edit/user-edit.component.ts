import { CommonModule, Location } from '@angular/common';
import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute, Router } from '@angular/router';
import { finalize } from 'rxjs/operators';
import { User, UserService } from '../user.service';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatOptionModule } from '@angular/material/core';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSelectModule } from '@angular/material/select';
import { RoleDto, RoleService } from '../../auth/role.service';

@Component({
    selector: 'app-user-edit',
    imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
    MatSelectModule,
    MatOptionModule,
    MatTooltipModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
],
    templateUrl: './user-edit.component.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrls: ['./user-edit.component.scss']
})
export class UserEditComponent implements OnInit {
    form!: FormGroup;
    isCreateMode: boolean = true;
    username: string | null = null;
    isLoading: boolean = false;

    roles: RoleDto[] = [];

    constructor(
        private fb: FormBuilder,
        private route: ActivatedRoute,
        private location: Location,
        private roleService: RoleService,
        private userService: UserService,
        private snackBar: MatSnackBar
    ) { }

    ngOnInit(): void {
        this.username = this.route.snapshot.paramMap.get('username');
        this.isCreateMode = this.username === '__NEW__';

        this.roleService.getAll().subscribe({
            next: roles => this.roles = roles,
            error: error => {
                this.snackBar.open('Error loading roles.', 'Close', { duration: 3000 });
                console.error('Error loading roles:', error);
            }
        });

        this.form = this.fb.group({
            username: [{ value: '', disabled: !this.isCreateMode }, Validators.required],
            email: ['', [Validators.required, Validators.email]],
            name: ['', Validators.required],
            disabled: [false],
            roles: [[]],
            password: [''] // Only for creation/update, not typically returned
        });

        if (!this.isCreateMode && this.username) {
            this.isLoading = true;
            this.userService.get(this.username).pipe(
                finalize(() => this.isLoading = false)
            ).subscribe({
                next: (user: User) => {
                    this.form.patchValue(user);
                    // Clear password field for security, as it's not meant to be displayed
                    this.form.get('password')?.setValue('');
                },
                error: error => {
                    this.snackBar.open('Error loading user data.', 'Close', { duration: 3000 });
                    console.error('Error loading user:', error);
                    this.location.back();
                }
            });
        }
    }

    save(): void {
        if (this.form.invalid) {
            this.form.markAllAsTouched();
            this.snackBar.open('Please correct the form errors.', 'Close', { duration: 3000 });
            return;
        }

        this.isLoading = true;
        const userValue: User = this.form.getRawValue(); // Use getRawValue to include disabled fields

        if (this.isCreateMode) {
            this.userService.create(userValue).pipe(
                finalize(() => this.isLoading = false)
            ).subscribe({
                next: () => {
                    this.snackBar.open('User created successfully!', 'Close', { duration: 3000 });
                    this.location.back();
                },
                error: error => {
                    this.snackBar.open('Error creating user.', 'Close', { duration: 3000 });
                    console.error('Error creating user:', error);
                }
            });
        } else if (this.username) {
            if (!userValue.password) {
                delete userValue.password;
            }
            this.userService.update(this.username, userValue).pipe(
                finalize(() => this.isLoading = false)
            ).subscribe({
                next: () => {
                    this.snackBar.open('User updated successfully!', 'Close', { duration: 3000 });
                    this.location.back();
                },
                error: error => {
                    this.snackBar.open('Error updating user.', 'Close', { duration: 3000 });
                    console.error('Error updating user:', error);
                }
            });
        }
    }

    cancel(): void {
        this.location.back();
    }

    onUsernameBlur() {
        const usernameValue = this.form.get('username')?.value;
        if (usernameValue && usernameValue.includes('@')) {
            this.form.patchValue({
                email: usernameValue.toLowerCase()
            });
        }
    }

    onSubmit(): void {
        this.save();
    }

    onClose(): void {
        this.location.back();
    }

}
