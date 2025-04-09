I'll enhance the program to handle cases where participants aren't enough for the original team compositions. The improved version will:

1. First try to form teams with the original composition
2. If not enough participants, adjust to minimum required roles
3. Distribute remaining participants to teams that can benefit most
4. Prioritize adding members of the same role to maintain balance

Here's the updated code:

```python
import pandas as pd
import random
from collections import defaultdict

class HackathonTeamFormation:
    def __init__(self, excel_file):
        # Read the Excel file
        self.df = pd.read_excel(excel_file)
        self.participants = self.df.to_dict('records')
        
        # Group participants by role
        self.by_role = defaultdict(list)
        for p in self.participants:
            self.by_role[p['role'].lower()].append(p)
    
    def show_participant_stats(self):
        """Show statistics about available participants"""
        print("\nAvailable Participants by Role:")
        for role, people in self.by_role.items():
            print(f"{role.capitalize()}: {len(people)}")
        
        print("\nExperience Distribution:")
        print(self.df['experience'].value_counts())
        
        print("\nEvaluation Score Stats:")
        print(self.df['evaluation score'].describe())
    
    def form_teams(self, team_compositions, min_requirements=None):
        """
        Form teams with flexible composition when participants are insufficient
        
        Args:
            team_compositions: List of dicts specifying ideal roles for each team
            min_requirements: Dict specifying minimum required roles across all teams
                             Example: {'full stack': 1, 'tester': 1}
                             If None, will use first team composition as min requirements
        """
        if min_requirements is None:
            # Use first team composition as minimum requirements
            min_requirements = {k: 1 for k in team_compositions[0].keys()}
        
        # First pass: try to form teams with original composition
        teams = []
        remaining_participants = self.participants.copy()
        original_composition_success = True
        
        for comp in team_compositions:
            team = []
            possible = True
            
            for role, count in comp.items():
                role_lower = role.lower()
                available = [p for p in remaining_participants if p['role'].lower() == role_lower]
                
                if len(available) < count:
                    possible = False
                    break
                
                # Select top performers first
                selected = sorted(available, key=lambda x: x['evaluation score'], reverse=True)[:count]
                team.extend(selected)
                
                for p in selected:
                    remaining_participants.remove(p)
            
            if possible:
                teams.append(team)
            else:
                original_composition_success = False
                break
        
        if not original_composition_success:
            print("\nNot enough participants for ideal composition. Trying with minimum requirements...")
            # Reset and try with minimum requirements
            teams = []
            remaining_participants = self.participants.copy()
            
            for comp in team_compositions:
                team = []
                
                # First fill minimum requirements
                for role, min_count in min_requirements.items():
                    role_lower = role.lower()
                    available = [p for p in remaining_participants if p['role'].lower() == role_lower]
                    count = min(min_count, len(available))
                    
                    if count > 0:
                        selected = sorted(available, key=lambda x: x['evaluation score'], reverse=True)[:count]
                        team.extend(selected)
                        
                        for p in selected:
                            remaining_participants.remove(p)
                
                # Then try to fill remaining roles from original composition
                for role, count in comp.items():
                    role_lower = role.lower()
                    current_count = sum(1 for m in team if m['role'].lower() == role_lower)
                    needed = count - current_count
                    
                    if needed > 0:
                        available = [p for p in remaining_participants if p['role'].lower() == role_lower]
                        count = min(needed, len(available))
                        
                        if count > 0:
                            selected = sorted(available, key=lambda x: x['evaluation score'], reverse=True)[:count]
                            team.extend(selected)
                            
                            for p in selected:
                                remaining_participants.remove(p)
                
                teams.append(team)
        
        # Distribute remaining participants to teams that can benefit most
        if remaining_participants:
            print("\nDistributing remaining participants to teams...")
            remaining_participants.sort(key=lambda x: x['evaluation score'], reverse=True)
            
            for p in remaining_participants:
                # Find team with lowest average score that has same role member
                best_team_idx = None
                lowest_avg = float('inf')
                p_role = p['role'].lower()
                
                for i, team in enumerate(teams):
                    # Calculate current average score
                    if not team:
                        continue
                    avg_score = sum(m['evaluation score'] for m in team) / len(team)
                    
                    # Check if team has same role member
                    has_same_role = any(m['role'].lower() == p_role for m in team)
                    
                    if has_same_role and avg_score < lowest_avg:
                        lowest_avg = avg_score
                        best_team_idx = i
                
                if best_team_idx is not None:
                    teams[best_team_idx].append(p)
                    remaining_participants.remove(p)
                else:
                    # If no team has same role, add to smallest team
                    smallest_team_idx = min(range(len(teams)), key=lambda i: len(teams[i]))
                    teams[smallest_team_idx].append(p)
                    remaining_participants.remove(p)
        
        return teams, remaining_participants
    
    def print_teams(self, teams):
        """Print the formed teams in a readable format"""
        for i, team in enumerate(teams, 1):
            print(f"\nTeam {i}:")
            print("-" * 30)
            total_score = 0
            role_count = defaultdict(int)
            
            for member in team:
                print(f"{member['name']} ({member['role']}, Exp: {member['experience']}, Score: {member['evaluation score']})")
                total_score += member['evaluation score']
                role_count[member['role']] += 1
            
            avg_score = total_score / len(team) if team else 0
            print("\nRole Distribution:")
            for role, count in role_count.items():
                print(f"{role}: {count}")
            print(f"\nTotal Team Score: {total_score:.1f}, Average: {avg_score:.1f}")
            print("-" * 30)
    
    def balance_teams(self, teams):
        """Balance teams by both experience and evaluation scores"""
        improved = True
        max_iterations = 100
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            # Calculate current team metrics
            team_metrics = []
            for team in teams:
                if not team:
                    team_metrics.append({'avg_score': 0, 'avg_exp': 0})
                    continue
                
                total_score = sum(m['evaluation score'] for m in team)
                total_exp = sum(m['experience'] for m in team)
                team_metrics.append({
                    'avg_score': total_score / len(team),
                    'avg_exp': total_exp / len(team)
                })
            
            # Try to find beneficial swaps
            for i in range(len(teams)):
                for j in range(i+1, len(teams)):
                    if not teams[i] or not teams[j]:
                        continue
                    
                    # Find candidates for swapping
                    for m1 in teams[i]:
                        for m2 in teams[j]:
                            if m1['role'] == m2['role']:
                                # Calculate potential new averages
                                new_avg_i_score = (team_metrics[i]['avg_score'] * len(teams[i]) - m1['evaluation score'] + m2['evaluation score']) / len(teams[i])
                                new_avg_j_score = (team_metrics[j]['avg_score'] * len(teams[j]) - m2['evaluation score'] + m1['evaluation score']) / len(teams[j])
                                
                                new_avg_i_exp = (team_metrics[i]['avg_exp'] * len(teams[i]) - m1['experience'] + m2['experience']) / len(teams[i])
                                new_avg_j_exp = (team_metrics[j]['avg_exp'] * len(teams[j]) - m2['experience'] + m1['experience']) / len(teams[j])
                                
                                # Calculate current and potential imbalances
                                current_imbalance = abs(team_metrics[i]['avg_score'] - team_metrics[j]['avg_score']) + abs(team_metrics[i]['avg_exp'] - team_metrics[j]['avg_exp'])
                                new_imbalance = abs(new_avg_i_score - new_avg_j_score) + abs(new_avg_i_exp - new_avg_j_exp)
                                
                                if new_imbalance < current_imbalance:
                                    # Perform the swap
                                    teams[i].remove(m1)
                                    teams[j].remove(m2)
                                    teams[i].append(m2)
                                    teams[j].append(m1)
                                    improved = True
                                    break
                        
                        if improved:
                            break
                    if improved:
                        break
                if improved:
                    break
        
        return teams

# Example usage
if __name__ == "__main__":
    # Initialize with your Excel file
    team_former = HackathonTeamFormation("hackathon_participants.xlsx")
    
    # Show participant statistics
    team_former.show_participant_stats()
    
    # Define your team compositions
    team_compositions = [
        {'Full Stack': 2, 'Tester': 1, 'AI Engineer': 1},
        {'Full Stack': 2, 'Tester': 1, 'AI Engineer': 1},
        {'Full Stack': 1, 'Tester': 2, 'AI Engineer': 1},
        {'Full Stack': 1, 'Tester': 1, 'AI Engineer': 2}
    ]
    
    # Define minimum requirements (at least 1 of each key role per team)
    min_requirements = {'Full Stack': 1, 'Tester': 1, 'AI Engineer': 1}
    
    # Form teams
    teams, remaining = team_former.form_teams(team_compositions, min_requirements)
    
    # Balance teams
    balanced_teams = team_former.balance_teams(teams)
    
    # Print the teams
    print("\nFinal Teams:")
    team_former.print_teams(balanced_teams)
    
    # Print remaining participants (should be empty after distribution)
    if remaining:
        print("\nRemaining Participants After Distribution:")
        for p in remaining:
            print(f"{p['name']} ({p['role']}, Score: {p['evaluation score']})")
    else:
        print("\nAll participants have been assigned to teams.")
```

## Key Improvements:

1. **Flexible Team Formation**:
   - First attempts to form teams with ideal composition
   - Falls back to minimum requirements if participants are insufficient
   - Minimum requirements can be specified or default to 1 of each role

2. **Remaining Participant Distribution**:
   - Distributes leftover participants to teams that:
     - Have members of the same role (to maintain role balance)
     - Have the lowest average score (to boost weaker teams)
   - Falls back to adding to smallest team if no same-role teams exist

3. **Enhanced Balancing**:
   - New balancing algorithm considers both experience and evaluation scores
   - Attempts to minimize differences between teams on both metrics
   - Uses a more sophisticated swap-based approach

4. **Better Reporting**:
   - Shows role distribution within each team
   - Clearly indicates when falling back to minimum requirements
   - Tracks distribution of remaining participants

## Usage Instructions:

1. Prepare your Excel file with columns: name, email, phone, role, experience, evaluation score
2. Define your ideal team compositions in `team_compositions`
3. Set minimum requirements in `min_requirements` (or leave as None to use defaults)
4. The program will:
   - First try to form ideal teams
   - If not possible, form teams with minimum requirements
   - Distribute any remaining participants optimally
   - Balance teams for fairness
   - Provide detailed output of the final teams

This version handles edge cases better and ensures all participants are used effectively while maintaining as much balance as possible between teams.
