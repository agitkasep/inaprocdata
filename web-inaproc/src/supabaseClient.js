import { createClient } from '@supabase/supabase-js';

// Masukkan kredensial proyek Supabase Anda (Gunakan URL dan Key yang sama dengan skrip Python)
const supabaseUrl = 'https://ncczkucvpxqvnizluumb.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5jY3prdWN2cHhxdm5pemx1dW1iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODMyMzQ2MjUsImV4cCI6MjA5ODgxMDYyNX0.ffw4plK3mdlwoUswD_uSBMISnKoGYNtav6d2IBnXPCQ';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);